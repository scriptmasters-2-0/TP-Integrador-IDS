# articulos_servicio.py
# Funciones de servicio para consumir endpoints /articulos
from servicios.api_client import delete_json, get_json, patch_json, post_json, put_json

TIMEOUT = 5


def obtener_articulos(params=None, token=None):
    """GET /articulos
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json("/articulos", token=token, params=params)
    if error:
        return []
    return payload or []


def crear_articulo(articulo_data, token=None):
    """POST /articulos
    Devuelve el JSON creado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = post_json("/articulos", articulo_data, token=token)
    if error:
        return {}
    return payload or {}


def obtener_articulo(articulo_id, token=None):
    """GET /articulos/{id}
    Devuelve el JSON del ítem en caso de éxito, {} en caso de fallo.
    """
    payload, error = get_json(f"/articulos/{articulo_id}", token=token)
    if error:
        return {}
    return payload or {}


def actualizar_articulo(articulo_id, articulo_data, token=None):
    """PUT /articulos/{id}
    Devuelve el JSON actualizado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = put_json(f"/articulos/{articulo_id}", articulo_data, token=token)
    if error:
        return {}
    return payload or {}


def eliminar_articulo(articulo_id, token=None):
    """DELETE /articulos/{id}
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = delete_json(f"/articulos/{articulo_id}", token=token)
    if error:
        return {}
    return True


def establecer_condicion_articulo(articulo_id, condition_data, token=None):
    """PATCH /articulos/{id}/condition
    condition_data: dict (ej., {"condition": "good"})
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = patch_json(f"/articulos/{articulo_id}/condition", condition_data, token=token)
    if error:
        return {}
    return True
