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
    normalized = path if path.startswith("/") else f"/{path}"
    return f"{config.BACKEND_URL}{normalized}"


def get_auth_headers(token=None):
    token = token or session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def get_json(path, token=None, params=None):
    """Ejecuta un GET y retorna (json, error)."""
    headers = get_auth_headers(token)
    try:
        response = requests.get(_build_url(path), headers=headers, params=params, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        error_msg = f"No se pudo conectar con backend: {exc}"
        logger.warning(error_msg)
        return None, error_msg

    if response.status_code >= HTTP_BAD_REQUEST:
        try:
            payload = response.json()
            detail = payload.get("error") or payload.get("message") or str(payload)
        except Exception:
            detail = response.text or f"HTTP {response.status_code}"
        logger.warning(f"Backend returned {response.status_code}: {detail}")
        return None, detail

    try:
        return response.json(), None
    except Exception:
        error_msg = "Respuesta inválida del backend"
        logger.error(error_msg)
        return None, error_msg


def post_json(path, data, token=None):
    """Ejecuta un POST JSON y retorna (json, error, status_code)."""
    headers = {"Content-Type": "application/json"}
    headers.update(get_auth_headers(token))
    try:
        response = requests.post(_build_url(path), json=data, headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        error_msg = f"No se pudo conectar con backend: {exc}"
        logger.warning(error_msg)
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
        logger.warning(f"Backend returned {response.status_code}: {detail}")
        return payload, detail, response.status_code

    return payload, None, response.status_code


def obtener_perfil_usuario():
    """Obtiene el perfil del usuario autenticado."""
    payload, error = get_json("/auth/me")
    if error:
        raise Exception(error)
    if isinstance(payload, dict):
        return payload.get("user", payload)
    raise Exception("Respuesta inválida del backend")


def obtener_prestamos():
    """Obtiene la lista de préstamos disponibles para el usuario autenticado."""
    payload, error = get_json("/loans")
    if error:
        raise Exception(error)
    return payload


def obtener_detalle_prestamo(loan_id):
    """Obtiene el detalle de un préstamo específico."""
    payload, error = get_json(f"/loans/{loan_id}")
    if error:
        raise Exception(error)
    return payload
