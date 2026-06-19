"""Cliente HTTP simple para consumir la API backend desde el frontend Flask."""

from __future__ import annotations

import logging

import requests
from flask import session

import config
from http_codes_and_messages import HTTP_BAD_REQUEST

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 8


def _build_url(path):
    """Descripción: función _build_url."""
    normalized = path if path.startswith("/") else f"/{path}"
    return f"{config.BACKEND_URL}{normalized}"


def get_auth_headers(token=None):
    """Descripción: función get_auth_headers."""
    token = token or session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


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
        try:
            payload = response.json()
            detail = payload.get("error") or payload.get("message") or str(payload)
        except Exception:
            detail = response.text or f"HTTP {response.status_code}"
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

    payload = None
    try:
        payload = response.json()
    except Exception:
        payload = None

    if response.status_code >= HTTP_BAD_REQUEST:
        detail = "Error al consumir backend"
        if isinstance(payload, dict):
            detail = payload.get("error") or payload.get("message") or str(payload)
        elif response.text:
            detail = response.text
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

    payload = None
    try:
        payload = response.json()
    except Exception:
        payload = None

    if response.status_code >= HTTP_BAD_REQUEST:
        detail = "Error al consumir backend"
        if isinstance(payload, dict):
            detail = payload.get("error") or payload.get("message") or str(payload)
        elif response.text:
            detail = response.text
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

    payload = None
    try:
        payload = response.json()
    except Exception:
        payload = None

    if response.status_code >= HTTP_BAD_REQUEST:
        detail = "Error al consumir backend"
        if isinstance(payload, dict):
            detail = payload.get("error") or payload.get("message") or str(payload)
        elif response.text:
            detail = response.text
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

    payload = None
    try:
        payload = response.json()
    except Exception:
        payload = None

    if response.status_code >= HTTP_BAD_REQUEST:
        detail = "Error al consumir backend"
        if isinstance(payload, dict):
            detail = payload.get("error") or payload.get("message") or str(payload)
        elif response.text:
            detail = response.text
        logger.warning("Backend returned %s: %s", response.status_code, detail)
        return payload, detail, response.status_code

    return payload, None, response.status_code


def obtener_perfil_usuario():
    """Obtiene el perfil del usuario autenticado."""
    payload, error = get_json("/auth/me")
    if error:
        raise Exception(error)
    if isinstance(payload, dict):
        return payload.get("usuario", payload)
    raise Exception("Respuesta inválida del backend")


def obtener_reservas():
    """Obtiene la lista de préstamos disponibles para el usuario autenticado."""
    payload, error = get_json("/reservas")
    if error:
        raise Exception(error)
    return payload


def obtener_detalle_reserva(reserva_id):
    """Obtiene el detalle de un préstamo específico."""
    payload, error = get_json(f"/reservas/{reserva_id}")
    if error:
        raise Exception(error)
    return payload
