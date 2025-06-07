FROM python:3.12.10-bullseye

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml pyproject.lock* ./

RUN uv venv .venv && \
    uv sync

COPY src/. .

CMD [".venv/bin/python", "main.py"]
