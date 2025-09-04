export const workletCode = `
  class StreamProcessor extends AudioWorkletProcessor {
    constructor() {
      super();
      // manipulate this to change the buffer size, 24000 is one per second
      // this.inputBuffer = new Float32Array(24000);
      this.inputBuffer = new Float32Array(128);
      this.inputOffset = 0;
      this.outputBuffers = [];
      this.isPlaying = false;

      this.port.onmessage = (event) => {
        if (event.data.type === 'playback') {
          this.outputBuffers.push(event.data.audio);
          this.isPlaying = true;
        }
        else if (event.data.type === 'stop_playback') {
         // Immediately stop playback and clear any queued audio
         this.outputBuffers = [];
         this.isPlaying = false;
         // Optionally notify main thread if you want
         this.port.postMessage({ type: 'done' });
        }
      };
    }

    process(inputs, outputs, parameters) {
      const input = inputs[0];
      if (input && input.length > 0) {
        const inputData = input[0];
        for (let i = 0; i < inputData.length; i++) {
          this.inputBuffer[this.inputOffset++] = inputData[i];

          if (this.inputOffset >= this.inputBuffer.length) {
            const outputData = new Int16Array(this.inputBuffer.length);
            for (let j = 0; j < this.inputBuffer.length; j++) {
              outputData[j] = Math.max(-1, Math.min(1, this.inputBuffer[j])) * 0x7FFF;
            }
            this.port.postMessage({
              type: 'input',
              audio: outputData
            });
            // manipulate this to change the buffer size, 24000 is one per second
            // this.inputBuffer = new Float32Array(24000);
            this.inputBuffer = new Float32Array(128);
            this.inputOffset = 0;
          }
        }
      }

      const output = outputs[0];
      if (output && output.length > 0 && this.isPlaying) {
        if (this.outputBuffers.length > 0) {
          const currentBuffer = this.outputBuffers[0];
          const chunkSize = Math.min(output[0].length, currentBuffer.length);

          const gain = 0.8;
          for (let channel = 0; channel < output.length; channel++) {
            const outputChannel = output[channel];
            for (let i = 0; i < chunkSize; i++) {
              outputChannel[i] = currentBuffer[i] * gain;
            }
          }

          if (chunkSize === currentBuffer.length) {
            this.outputBuffers.shift();
          } else {
            this.outputBuffers[0] = currentBuffer.slice(chunkSize);
          }
        }

        if (this.outputBuffers.length === 0) {
          this.isPlaying = false;
          this.port.postMessage({ type: 'done' });
        }
      }
      return true;
    }
  }

  try {
    registerProcessor('stream_processor', StreamProcessor);
  } catch (e) {
    // Check for registration error without relying on DOMException
    if (e && e.message && e.message.includes('is already registered')) {
      // Processor already registered, ignore the error
    } else {
      throw e;
    }
  }
`;

import { describe, it, expect } from 'vitest';

/**
 * Test framework note:
 * - Using Vitest (importing describe/it/expect). If your repository uses Jest instead,
 *   replace the import with `import { describe, it, expect } from '@jest/globals';`
 *   and the tests will work the same.
 */

type AnyFn = (...args: any[]) => any;

class FakePort {
  public onmessage: ((ev: { data: any }) => void) | null = null;
  public messages: any[] = [];
  postMessage(msg: any) {
    this.messages.push(msg);
  }
}

class FakeAudioWorkletProcessor {
  public port: FakePort;
  constructor() {
    this.port = new FakePort();
  }
}

function evaluateWorklet(code: string, registry = new Set<string>()) {
  const registerCalls: string[] = [];
  let capturedCtor: any = null;

  function registerProcessor(name: string, ctor: any) {
    registerCalls.push(name);
    if (registry.has(name)) {
      const err: any = new Error(`${name} is already registered`);
      // Ensure message contains the text the worklet checks for:
      err.message = `AudioWorkletProcessor with name '${name}' is already registered`;
      throw err;
    }
    registry.add(name);
    capturedCtor = ctor;
  }

  // Evaluate the worklet module code in a sandboxed Function scope
  const fn = new Function('AudioWorkletProcessor', 'registerProcessor', code + '\nreturn true;') as AnyFn;
  fn(FakeAudioWorkletProcessor, registerProcessor);

  return { ProcessorCtor: capturedCtor, registerCalls, registry };
}

function callProcessWithInput(inst: any, samples: number[]) {
  const inputs = [[Float32Array.from(samples)]];
  const outputs: any[] = []; // not needed for input path
  const parameters = {};
  return inst.process(inputs, outputs, parameters);
}

function callProcessWithOutput(inst: any, frames: number, channels = 1) {
  const outputChannels = Array.from({ length: channels }, () => new Float32Array(frames));
  const outputs = [outputChannels];
  const inputs: any[] = []; // no new input here
  const parameters = {};
  const ok = inst.process(inputs, outputs, parameters);
  return { ok, outputs: outputChannels };
}

describe('StreamProcessor worklet', () => {
  it('registers "stream_processor" without throwing and exposes a constructor', () => {
    const { ProcessorCtor, registerCalls } = evaluateWorklet(workletCode);
    expect(registerCalls).toEqual(['stream_processor']);
    expect(typeof ProcessorCtor).toBe('function');
  });

  it('ignores duplicate registration errors gracefully', () => {
    const shared = new Set<string>();
    const first = evaluateWorklet(workletCode, shared);
    expect(first.ProcessorCtor).toBeTypeOf('function');
    // Re-evaluate with the same registry; internal try/catch should swallow the error
    const second = evaluateWorklet(workletCode, shared);
    expect(second.ProcessorCtor).toBeTypeOf('function');
  });

  it('buffers microphone input and posts Int16 audio when threshold (128) is reached', () => {
    const { ProcessorCtor } = evaluateWorklet(workletCode);
    const inst: any = new ProcessorCtor();
    const port: FakePort = inst.port;

    // Feed 127 zeros first - should not flush
    callProcessWithInput(inst, new Array(127).fill(0));
    expect(port.messages.length).toBe(0);

    // Feed 1 sample of 1.0 to reach 128 and trigger postMessage
    callProcessWithInput(inst, [1.0]);

    expect(port.messages.length).toBe(1);
    const msg = port.messages[0];
    expect(msg.type).toBe('input');
    expect(msg.audio).toBeInstanceOf(Int16Array);
    expect((msg.audio as Int16Array).length).toBe(128);
    // Check a few representative samples for correct scaling/clamping
    const audio = msg.audio as Int16Array;
    // Early samples were zeros
    expect(audio[0]).toBe(0);
    expect(audio[100]).toBe(0);
    // Last sample was 1.0 -> 32767
    expect(audio[127]).toBe(32767);
  });

  it('clamps input values to [-1, 1] before scaling to Int16', () => {
    const { ProcessorCtor } = evaluateWorklet(workletCode);
    const inst: any = new ProcessorCtor();
    const port: FakePort = inst.port;

    // Build a 128-sample frame that starts with extreme values
    const pattern = [-2, -1, 0, 1, 2];
    const samples: number[] = [];
    while (samples.length < 128) samples.push(...pattern);
    samples.length = 128;

    callProcessWithInput(inst, samples);
    const msg = port.messages[0];
    const audio = msg.audio as Int16Array;

    // -2 clamps to -1 -> -32767
    expect(audio[0]).toBe(-32767);
    // -1 -> -32767
    expect(audio[1]).toBe(-32767);
    // 0 -> 0
    expect(audio[2]).toBe(0);
    // 1 -> 32767
    expect(audio[3]).toBe(32767);
    // 2 clamps to 1 -> 32767
    expect(audio[4]).toBe(32767);
  });

  it('writes playback audio to all output channels with 0.8 gain and drains buffers across calls', () => {
    const { ProcessorCtor } = evaluateWorklet(workletCode);
    const inst: any = new ProcessorCtor();
    const port: FakePort = inst.port;

    // Queue a small playback buffer of 5 samples
    const queued = Float32Array.from([-1, -0.5, 0, 0.5, 1]);
    port.onmessage?.({ data: { type: 'playback', audio: queued } });

    // First render call: request 3 frames, 2 channels
    const { outputs: out1 } = callProcessWithOutput(inst, 3, 2);
    const expected1 = [-0.8, -0.4, 0];
    expect(Array.from(out1[0])).toEqual(expected1);
    expect(Array.from(out1[1])).toEqual(expected1);

    // Second render call: request remaining 2 frames, 2 channels; should also emit "done"
    const { outputs: out2 } = callProcessWithOutput(inst, 2, 2);
    const expected2 = [0.4, 0.8];
    expect(Array.from(out2[0])).toEqual(expected2);
    expect(Array.from(out2[1])).toEqual(expected2);

    // Playback finished -> isPlaying false and "done" message posted
    expect(inst.isPlaying).toBe(false);
    const doneMsg = port.messages.find(m => m && m.type === 'done');
    expect(doneMsg).toBeTruthy();
  });

  it('stop_playback message immediately clears queue and posts done', () => {
    const { ProcessorCtor } = evaluateWorklet(workletCode);
    const inst: any = new ProcessorCtor();
    const port: FakePort = inst.port;

    // Queue two buffers
    port.onmessage?.({ data: { type: 'playback', audio: Float32Array.from([0.1, 0.2, 0.3]) } });
    port.onmessage?.({ data: { type: 'playback', audio: Float32Array.from([0.4, 0.5]) } });
    expect(inst.outputBuffers.length).toBe(2);
    expect(inst.isPlaying).toBe(true);

    // Stop immediately
    port.onmessage?.({ data: { type: 'stop_playback' } });
    expect(inst.outputBuffers.length).toBe(0);
    expect(inst.isPlaying).toBe(false);
    const doneMsg = port.messages.find(m => m && m.type === 'done');
    expect(doneMsg).toBeTruthy();
  });

  it('returns true from process under various conditions', () => {
    const { ProcessorCtor } = evaluateWorklet(workletCode);
    const inst: any = new ProcessorCtor();

    // No input/output
    expect(inst.process([], [], {})).toBe(true);

    // Only input
    expect(inst.process([[new Float32Array(0)]], [], {})).toBe(true);

    // Only output (not playing)
    const outs = [[new Float32Array(4)]];
    expect(inst.process([], outs, {})).toBe(true);
  });

  it('mirrors playback samples across multiple output channels', () => {
    const { ProcessorCtor } = evaluateWorklet(workletCode);
    const inst: any = new ProcessorCtor();
    const port: FakePort = inst.port;

    // Queue 3 samples
    port.onmessage?.({ data: { type: 'playback', audio: Float32Array.from([0, 1, -1]) } });

    const { outputs } = callProcessWithOutput(inst, 3, 2);
    const expected = [0, 0.8, -0.8];
    expect(Array.from(outputs[0])).toEqual(expected);
    expect(Array.from(outputs[1])).toEqual(expected);
  });
});