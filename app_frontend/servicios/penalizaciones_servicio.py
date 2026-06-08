# penalizaciones_servicio.py
# Funciones de servicio para consumir endpoints /penalizaciones
from servicios.api_client import get_json, post_json, put_json, patch_json

TIMEOUT = 5


def obtener_penalizaciones(params=None, token=None):
    """GET /penalizaciones
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json("/penalizaciones", token=token, params=params)
    if error:
        return []
    return payload or []


def crear_penalizacion(penalty_data, token=None):
    """POST /penalizaciones
    Devuelve el JSON de la penalización creada en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = post_json("/penalizaciones", penalty_data, token=token)
    if error:
        return {}
    return payload or {}


def obtener_penalizacion(penalty_id, token=None):
    """GET /penalizaciones/{id}
    Devuelve el JSON de la penalización en caso de éxito, {} en caso de fallo.
    """
    payload, error = get_json(f"/penalizaciones/{penalty_id}", token=token)
    if error:
        return {}
    return payload or {}


def actualizar_penalizacion(penalty_id, penalty_data, token=None):
    """PUT /penalizaciones/{id}
    Devuelve el JSON actualizado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = put_json(f"/penalizaciones/{penalty_id}", penalty_data, token=token)
    if error:
        return {}
    return payload or {}


def actualizar_parcial_penalizacion(penalty_id, patch_data, token=None):
    """PATCH /penalizaciones/{id}
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = patch_json(f"/penalizaciones/{penalty_id}", patch_data, token=token)
    if error:
        return {}
    return True
