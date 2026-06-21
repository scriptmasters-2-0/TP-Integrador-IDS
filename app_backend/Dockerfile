ARG MYPORT
ARG PYTHON_VERSION=3.14.3
FROM python:${PYTHON_VERSION}-slim AS base

# Mantener la salida de Python sin buffer y evitar archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    python -m pip install uv && \
    uv sync --locked --no-dev --no-install-project

RUN groupadd --system tpIntegral && useradd --system -g tpIntegral tpIntegral

COPY . .

RUN chown -R tpIntegral:tpIntegral /app

EXPOSE ${MYPORT}

USER tpIntegral

CMD ["python", "app.py"]
