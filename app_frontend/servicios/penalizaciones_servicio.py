# penalizaciones_servicio.py
# Funciones de servicio para consumir endpoints /penalizaciones
from servicios.api_client import get_json, post_json, patch_json
from servicios.paginacion_servicio import extraer_data_paginada


def obtener_penalizaciones(params=None, token=None):
    """GET /penalizaciones
    Devuelve (payload, error) con [] como fallback.
    """
    payload, error = get_json("/penalizaciones", token=token, params=params)
    return extraer_data_paginada(payload), error


def obtener_penalizaciones_paginadas(params=None, token=None):
    """Obtiene penalizaciones preservando metadata y links HATEOAS."""
    payload, error = get_json("/penalizaciones", token=token, params=params)
    if error:
        return {"data": [], "pagination": {}, "links": {}}, error
    if isinstance(payload, dict):
        return payload, None
    return {"data": extraer_data_paginada(payload), "pagination": {}, "links": {}}, None


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


def actualizar_parcial_penalizacion(penalty_id, patch_data, token=None):
    """PATCH /penalizaciones/{id}
    Devuelve (ok, error, status) para que la ruta decida el flujo.
    """
    payload, error, status = patch_json(f"/penalizaciones/{penalty_id}", patch_data, token=token)
    if error:
        return False, error, status
    return True, None, status
