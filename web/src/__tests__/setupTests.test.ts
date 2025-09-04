/**
 * Tests for Jest setup behaviors defined in web/src/setupTests.ts
 * Frameworks:
 *  - Test runner: Jest
 *  - Matchers: @testing-library/jest-dom
 */

import "@testing-library/jest-dom";

// Helper to intercept stderr writes so we can assert pass-through vs suppression
function interceptStderr<T>(fn: () => T) {
  const original = process.stderr.write as any;
  const calls: Array<string | Buffer> = [];
  (process.stderr.write as any) = ((chunk: any, ..._rest: any[]) => {
    calls.push(chunk);
    return true;
  }) as any;

  let result: T;
  try {
    result = fn();
  } finally {
    (process.stderr.write as any) = original;
  }
  return { calls, result };
}

describe("global mocks from setupTests", () => {
  test("jest-dom matchers are available", () => {
    const el = document.createElement("div");
    document.body.appendChild(el);
    expect(el).toBeInTheDocument(); // Provided by @testing-library/jest-dom
  });

  test("ResizeObserver is a mocked constructor with observe/unobserve/disconnect", () => {
    // @ts-expect-no-error - provided by setup file
    const Ctor = (global as any).ResizeObserver;
    expect(typeof Ctor).toBe("function");
    expect(jest.isMockFunction(Ctor)).toBe(true);

    const instance = new Ctor(() => {});
    expect(instance).toBeDefined();
    expect(typeof instance.observe).toBe("function");
    expect(typeof instance.unobserve).toBe("function");
    expect(typeof instance.disconnect).toBe("function");
    expect(jest.isMockFunction(instance.observe)).toBe(true);
    expect(jest.isMockFunction(instance.unobserve)).toBe(true);
    expect(jest.isMockFunction(instance.disconnect)).toBe(true);

    const target = document.createElement("div");
    instance.observe(target);
    instance.unobserve(target);
    instance.disconnect();

    expect(instance.observe).toHaveBeenCalledTimes(1);
    expect(instance.unobserve).toHaveBeenCalledTimes(1);
    expect(instance.disconnect).toHaveBeenCalledTimes(1);
  });

  test("IntersectionObserver is a mocked constructor with observe/unobserve/disconnect", () => {
    // @ts-expect-no-error - provided by setup file
    const Ctor = (global as any).IntersectionObserver;
    expect(typeof Ctor).toBe("function");
    expect(jest.isMockFunction(Ctor)).toBe(true);

    const instance = new Ctor(() => {});
    expect(instance).toBeDefined();
    expect(typeof instance.observe).toBe("function");
    expect(typeof instance.unobserve).toBe("function");
    expect(typeof instance.disconnect).toBe("function");
    expect(jest.isMockFunction(instance.observe)).toBe(true);
    expect(jest.isMockFunction(instance.unobserve)).toBe(true);
    expect(jest.isMockFunction(instance.disconnect)).toBe(true);

    const target = document.createElement("div");
    instance.observe(target);
    instance.unobserve(target);
    instance.disconnect();

    expect(instance.observe).toHaveBeenCalledTimes(1);
    expect(instance.unobserve).toHaveBeenCalledTimes(1);
    expect(instance.disconnect).toHaveBeenCalledTimes(1);
  });

  test("window.matchMedia returns a MediaQueryList-like mock", () => {
    expect(typeof window.matchMedia).toBe("function");
    expect(jest.isMockFunction(window.matchMedia)).toBe(true);

    const query = "(max-width: 600px)";
    const mql = window.matchMedia(query);

    expect(mql).toBeDefined();
    expect(mql.matches).toBe(false);
    expect(mql.media).toBe(query);

    // Legacy and modern listener APIs exist and are mock functions
    expect(typeof mql.addListener).toBe("function");
    expect(typeof mql.removeListener).toBe("function");
    expect(jest.isMockFunction(mql.addListener)).toBe(true);
    expect(jest.isMockFunction(mql.removeListener)).toBe(true);

    expect(typeof mql.addEventListener).toBe("function");
    expect(typeof mql.removeEventListener).toBe("function");
    expect(typeof mql.dispatchEvent).toBe("function");
    expect(jest.isMockFunction(mql.addEventListener)).toBe(true);
    expect(jest.isMockFunction(mql.removeEventListener)).toBe(true);
    expect(jest.isMockFunction(mql.dispatchEvent)).toBe(true);

    // Calls are tracked
    const handler = jest.fn();
    mql.addEventListener("change", handler);
    expect(mql.addEventListener).toHaveBeenCalledWith("change", handler);
  });

  test("window.matchMedia is writable (as configured in setup)", () => {
    const original = window.matchMedia;
    const stub = jest.fn().mockReturnValue({
      matches: true,
      media: "all",
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    } as any);

    try {
      // Should not throw because writable: true
      // @ts-ignore - we intentionally reassign to verify configurability
      window.matchMedia = stub;
      expect(window.matchMedia).toBe(stub);
      const mql = window.matchMedia("all");
      expect(mql.matches).toBe(true);
    } finally {
      // Restore original for subsequent tests
      // @ts-ignore
      window.matchMedia = original;
    }
  });
});

describe("console suppression behavior from setupTests", () => {
  test("suppresses ReactDOM.render deprecation errors via console.error", () => {
    const { calls } = interceptStderr(() => {
      // This specific substring should be suppressed by the wrapper
      console.error("Warning: ReactDOM.render is deprecated and will be removed in React 18");
    });

    // Nothing should have been written to stderr
    expect(calls.length).toBe(0);
  });

  test("passes through other console.error messages", () => {
    const { calls } = interceptStderr(() => {
      console.error("Non-suppressed error: Boom!");
    });

    // At least one write should occur and include our message
    expect(calls.length).toBeGreaterThan(0);
    expect(calls.some(c => String(c).includes("Non-suppressed error: Boom!"))).toBe(true);
  });

  test("suppresses componentWillReceiveProps rename warnings via console.warn", () => {
    const { calls } = interceptStderr(() => {
      console.warn("componentWillReceiveProps has been renamed and is not recommended for use.");
    });

    expect(calls.length).toBe(0);
  });

  test("passes through other console.warn messages", () => {
    const { calls } = interceptStderr(() => {
      console.warn("Heads up: this is a regular warning.");
    });

    expect(calls.length).toBeGreaterThan(0);
    expect(calls.some(c => String(c).includes("Heads up: this is a regular warning."))).toBe(true);
  });
});