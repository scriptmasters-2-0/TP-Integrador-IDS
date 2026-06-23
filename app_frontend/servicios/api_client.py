"""Cliente HTTP simple para consumir la API backend desde el frontend Flask."""

from __future__ import annotations

import logging

import requests
from flask import session

import config
from http_codes_and_messages import HTTP_BAD_REQUEST

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 8
ERRORES_TOKEN = {
    "Token expirado",
    "Token inválido",
    "Tipo de token incorrecto",
}


def _build_url(path):
    """Descripción: función _build_url."""
    normalized = path if path.startswith("/") else f"/{path}"
    return f"{config.BACKEND_URL}{normalized}"


def get_auth_headers(token=None):
    """Descripción: función get_auth_headers."""
    token = token or session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _error_token(error):
    return error in ERRORES_TOKEN


def _limpiar_sesion_token(error):
    if _error_token(error):
        session.clear()


def _extraer_error_back(response, payload=None, default="Error al consumir backend"):
    if isinstance(payload, dict):
        return payload.get("error") or payload.get("message") or str(payload)

    if response.text:
        return response.text

    return default


def _parsear_payload(response):
    try:
        return response.json()
    except Exception:
        return None


def get_json(path, token=None, params=None):
    """Ejecuta un GET y retorna (json, error)."""
    headers = get_auth_headers(token)
    try:
        response = requests.get(_build_url(path), headers=headers, params=params, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        error_msg = f"No se pudo conectar con backend: {exc}"
        logger.warning("No se pudo conectar con backend: %s", exc)
        return None, error_msg

    if response.status_code >= HTTP_BAD_REQUEST:
        payload = _parsear_payload(response)
        detail = _extraer_error_back(
            response,
            payload,
            default=f"HTTP {response.status_code}",
        )
        _limpiar_sesion_token(detail)
        logger.warning("Backend devolvió %s: %s", response.status_code, detail)
        return None, detail

    try:
        return response.json(), None
    except Exception:
        error_msg = "Respuesta inválida del backend"
        logger.error("Respuesta inválida del backend")
        return None, error_msg


def post_json(path, data, token=None):
    """Ejecuta un POST JSON y retorna (json, error, status_code)."""
    headers = {"Content-Type": "application/json"}
    headers.update(get_auth_headers(token))
    try:
        response = requests.post(_build_url(path), json=data, headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        error_msg = f"No se pudo conectar con backend: {exc}"
        logger.warning("No se pudo conectar con backend: %s", exc)
        return None, error_msg, 0

    payload = _parsear_payload(response)

    if response.status_code >= HTTP_BAD_REQUEST:
        detail = _extraer_error_back(response, payload)
        _limpiar_sesion_token(detail)
        logger.warning("Backend devolvió %s: %s", response.status_code, detail)
        return payload, detail, response.status_code

    return payload, None, response.status_code


def patch_json(path, data, token=None):
    """Ejecuta un PATCH JSON y retorna (json, error, status_code)."""
    headers = {"Content-Type": "application/json"}
    headers.update(get_auth_headers(token))
    try:
        response = requests.patch(_build_url(path), json=data, headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        error_msg = f"No se pudo conectar con backend: {exc}"
        logger.warning("No se pudo conectar con backend: %s", exc)
        return None, error_msg, 0

    payload = _parsear_payload(response)

    if response.status_code >= HTTP_BAD_REQUEST:
        detail = _extraer_error_back(response, payload)
        _limpiar_sesion_token(detail)
        logger.warning("Backend devolvió %s: %s", response.status_code, detail)
        return payload, detail, response.status_code

    return payload, None, response.status_code


def put_json(path, data, token=None):
    """Ejecuta un PUT JSON y retorna (json, error, status_code)."""
    headers = {"Content-Type": "application/json"}
    headers.update(get_auth_headers(token))
    try:
        response = requests.put(_build_url(path), json=data, headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        error_msg = f"No se pudo conectar con backend: {exc}"
        logger.warning("No se pudo conectar con backend: %s", exc)
        return None, error_msg, 0

    payload = _parsear_payload(response)

    if response.status_code >= HTTP_BAD_REQUEST:
        detail = _extraer_error_back(response, payload)
        _limpiar_sesion_token(detail)
        logger.warning("Backend devolvió %s: %s", response.status_code, detail)
        return payload, detail, response.status_code

    return payload, None, response.status_code


def delete_json(path, token=None):
    """Ejecuta un DELETE y retorna (json, error, status_code)."""
    headers = get_auth_headers(token)
    try:
        response = requests.delete(_build_url(path), headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        error_msg = f"No se pudo conectar con backend: {exc}"
        logger.warning("No se pudo conectar con backend: %s", exc)
        return None, error_msg, 0

    payload = _parsear_payload(response)

    if response.status_code >= HTTP_BAD_REQUEST:
        detail = _extraer_error_back(response, payload)
        _limpiar_sesion_token(detail)
        logger.warning("Backend devolvió %s: %s", response.status_code, detail)
        return payload, detail, response.status_code

    return payload, None, response.status_code
