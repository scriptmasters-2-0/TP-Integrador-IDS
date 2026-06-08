ARG MYPORT
ARG PYTHON_VERSION=3.14.3
FROM python:${PYTHON_VERSION}-slim as base

# Mantener la salida de Python sin buffer y evitar archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install .

RUN groupadd --system tpIntegral && useradd --system -g tpIntegral tpIntegral

COPY . .

RUN chown -R tpIntegral:tpIntegral /app

EXPOSE ${MYPORT}

USER tpIntegral

CMD ["python", "app.py"]
