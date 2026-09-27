FROM ros:humble-ros-base-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser runtime/ runtime/
COPY --chown=appuser:appuser examples/ examples/

USER appuser

CMD ["python", "runtime/prototype.py", "examples/prototype_stream.jsonl"]
