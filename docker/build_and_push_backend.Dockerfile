# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

ARG AIEXEC_IMAGE
FROM $AIEXEC_IMAGE

RUN rm -rf /app/.venv/aiexec/frontend

CMD ["python", "-m", "aiexec", "run", "--host", "0.0.0.0", "--port", "7860", "--backend-only"]
