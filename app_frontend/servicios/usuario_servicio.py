# usuario_servicio.py
# Funciones de servicio para consumir endpoints /usuarios
from servicios.api_client import get_json, post_json, put_json, delete_json
from servicios.paginacion_servicio import extraer_data_paginada

def obtener_usuarios(params=None, token=None):
    """GET /usuarios
    params: diccionario opcional para parámetros de consulta
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json("/usuarios", token=token, params=params)
    if error:
        return []
    return extraer_data_paginada(payload)


def obtener_usuarios_paginados(params=None, token=None):
    """Obtiene usuarios preservando metadata y links HATEOAS."""
    payload, error = get_json("/usuarios", token=token, params=params)
    if error:
        return {"data": [], "pagination": {}, "links": {}}, error
    if isinstance(payload, dict):
        return payload, None
    return {"data": extraer_data_paginada(payload), "pagination": {}, "links": {}}, None

def crear_usuario(usuario_data, token=None):
    """POST /usuarios
    usuario_data: dict
    Devuelve (payload, error, status) para que la ruta decida el flujo.
    """
    return post_json("/usuarios", usuario_data, token=token)

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
    Devuelve (payload, error, status) para que la ruta decida el flujo.
    """
    return put_json(f"/usuarios/{usuario_id}", usuario_data, token=token)


def eliminar_usuario(usuario_id, token=None):
    """DELETE /usuarios/{id}
    Devuelve (ok, error, status) para que la ruta decida el flujo.
    """
    payload, error, status = delete_json(f"/usuarios/{usuario_id}", token=token)
    if error:
        return False, error, status
    return True, None, status


def obtener_reservas_usuario(usuario_id, params=None, token=None):
    """GET /usuarios/{id}/reservas
    Devuelve (payload, error) con [] como fallback.
    """
    payload, error = get_json(f"/usuarios/{usuario_id}/reservas", token=token, params=params)
    return payload or [], error

def obtener_penalizaciones_usuario(usuario_id, params=None, token=None):
    """GET /usuarios/{id}/penalizaciones
    Devuelve una lista de penalizaciones del usuario en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json(f"/usuarios/{usuario_id}/penalizaciones", token=token, params=params)
    if error:
        return []
    return payload or []
