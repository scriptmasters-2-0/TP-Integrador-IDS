# auth_servicio.py
# Funciones de servicio para consumir endpoints /auth
from servicios.api_client import post_json, get_json


def crear_usuario(credentials):
    """POST /auth/logup
    credentials: dict (ej., {"nombre": "...", "email": "...", "carrera": "...", "contrasenia": "..."})
    Devuelve el JSON parseado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = post_json("/auth/logup", credentials)
    if error:
        return {}
    return payload or {}


def iniciar_sesion(credentials):
    """POST /auth/login
    credentials: dict (ej., {"nombre": "...", "contrasenia": "..."})
    Devuelve el JSON parseado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = autenticar_usuario(credentials)
    if error:
        return {}
    return payload or {}


def autenticar_usuario(credentials):
    """POST /auth/login y conserva payload, error y status."""
    return post_json("/auth/login", credentials)


def cerrar_sesion(token=None):
    """POST /auth/logout
    Devuelve el JSON parseado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = post_json("/auth/logout", {}, token=token)
    if error:
        return {}
    return payload or {}


def obtener_mi_perfil(token=None):
    """GET /auth/me
    Devuelve el JSON con la información del usuario en caso de éxito, {} en caso de fallo.
    """
    payload, error = get_json("/auth/me", token=token)
    if error:
        return {}
    return payload or {}
