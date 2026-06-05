"""Cliente HTTP simple para consumir la API backend desde el frontend Flask."""
from __future__ import annotations

from typing import Any
import requests
from flask import session
import config

DEFAULT_TIMEOUT = 8


def _build_url(path: str) -> str:
    normalized = path if path.startswith("/") else f"/{path}"
    return f"{config.BACKEND_URL}{normalized}"


def get_auth_headers(token: str | None = None) -> dict[str, str]:
    token = token or session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def get_json(path: str, token: str | None = None, params: dict[str, Any] | None = None) -> tuple[Any, str | None]:
    """Ejecuta un GET y retorna (json, error)."""
    headers = get_auth_headers(token)
    try:
        response = requests.get(
            _build_url(path), headers=headers, params=params, timeout=DEFAULT_TIMEOUT
        )
    except requests.RequestException as exc:
        return None, f"No se pudo conectar con backend: {exc}"

    if response.status_code >= 400:
        try:
            payload = response.json()
            detail = payload.get("error") or payload.get("message") or str(payload)
        except Exception:
            detail = response.text or f"HTTP {response.status_code}"
        return None, detail

    try:
        return response.json(), None
    except Exception:
        return None, "Respuesta inválida del backend"


def post_json(path: str, data: dict[str, Any], token: str | None = None) -> tuple[Any, str | None, int]:
    """Ejecuta un POST JSON y retorna (json, error, status_code)."""
    headers: dict[str, str] = {"Content-Type": "application/json"}
    headers.update(get_auth_headers(token))
    try:
        response = requests.post(
            _build_url(path), json=data, headers=headers, timeout=DEFAULT_TIMEOUT
        )
    except requests.RequestException as exc:
        return None, f"No se pudo conectar con backend: {exc}", 0

    payload: Any = None
    try:
        payload = response.json()
    except Exception:
        payload = None

    if response.status_code >= 400:
        detail = "Error al consumir backend"
        if isinstance(payload, dict):
            detail = payload.get("error") or payload.get("message") or str(payload)
        elif response.text:
            detail = response.text
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
