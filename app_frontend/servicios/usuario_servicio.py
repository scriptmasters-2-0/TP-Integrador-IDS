# usuario_servicio.py
# Funciones de servicio para consumir endpoints /usuarios
from servicios.api_client import get_json, post_json, put_json, delete_json, patch_json

TIMEOUT = 5

def obtener_usuarios(params=None, token=None):
    """GET /usuarios
    params: diccionario opcional para parámetros de consulta
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json("/usuarios", token=token, params=params)
    if error:
        return []
    return payload or []

def crear_usuario(usuario_data, token=None):
    """POST /usuarios
    usuario_data: dict
    Devuelve el JSON parseado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = post_json("/usuarios", usuario_data, token=token)
    if error:
        return {}
    return payload or {}

def obtener_usuario(usuario_id, token=None):
    """GET /usuarios/{id}
    Devuelve el JSON del usuario en caso de éxito, {} en caso de fallo.
    """
    payload, error = get_json(f"/usuarios/{usuario_id}", token=token)
    if error:
        return {}
    return payload or {}

def actualizar_usuario(usuario_id, usuario_data, token=None):
    """PUT /usuarios/{id}
    Devuelve el JSON actualizado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = put_json(f"/usuarios/{usuario_id}", usuario_data, token=token)
    if error:
        return {}
    return payload or {}


def eliminar_usuario(usuario_id, token=None):
    """DELETE /usuarios/{id}
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = delete_json(f"/usuarios/{usuario_id}", token=token)
    if error:
        return {}
    return True


def establecer_estado_usuario(usuario_id, status_data, token=None):
    """PATCH /usuarios/{id}/status
    status_data: dict (ej., {"active": True})
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = patch_json(f"/usuarios/{usuario_id}/status", status_data, token=token)
    if error:
        return {}
    return True


def obtener_reservas_usuario(usuario_id, params=None, token=None):
    """GET /usuarios/{id}/reservas
    Devuelve una lista de préstamos del usuario en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json(f"/usuarios/{usuario_id}/reservas", token=token, params=params)
    if error:
        return []
    return payload or []

def obtener_reservas_usuario_con_error(usuario_id, params=None, token=None):
    """GET /usuarios/{id}/reservas preservando el error para vistas."""
    payload, error = get_json(f"/usuarios/{usuario_id}/reservas", token=token, params=params)
    if error:
        return [], error
    return payload or [], None


def obtener_reservas_usuario_con_error(usuario_id, params=None, token=None):
    """GET /usuarios/{id}/reservas preservando el error para vistas."""
    payload, error = get_json(f"/usuarios/{usuario_id}/reservas", token=token, params=params)
    if error:
        return [], error
    return payload or [], None


def obtener_penalizaciones_usuario(usuario_id, params=None, token=None):
    """GET /usuarios/{id}/penalizaciones
    Devuelve una lista de penalizaciones del usuario en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json(f"/usuarios/{usuario_id}/penalizaciones", token=token, params=params)
    if error:
        return []
    return payload or []
