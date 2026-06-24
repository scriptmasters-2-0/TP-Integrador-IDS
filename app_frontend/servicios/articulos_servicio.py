# articulos_servicio.py
# Funciones de servicio para consumir endpoints /articulos
from servicios.api_client import get_json, post_json, put_json, delete_json
from servicios.paginacion_servicio import extraer_data_paginada


def obtener_articulos(params=None, token=None):
    """GET /articulos
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json("/articulos", token=token, params=params)
    if error:
        return []
    return extraer_data_paginada(payload)


def obtener_articulos_paginados(params=None, token=None):
    """GET /articulos
    Obtiene el listado paginado de articulos.
    """
    payload, error = get_json("/articulos", token=token, params=params)

    if error:
        return {}
    if not isinstance(payload, dict):
        return {}

    return {
        "datos": extraer_data_paginada(payload),
        "pagination": payload.get("pagination") or {},
        "links": payload.get("links") or {},
    }


def crear_articulo(articulo_data, token=None):
    """POST /articulos
    Devuelve el JSON creado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = post_json("/articulos", articulo_data, token=token)
    if error:
        return {}
    return payload or {}


def obtener_articulo(articulo_id, token=None, params=None):
    """GET /articulos/{id}
    Devuelve (payload, error) con {} como fallback.
    """
    payload, error = get_json(f"/articulos/{articulo_id}", token=token, params=params)
    return payload or {}, error


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
    Devuelve (ok, error, status) para que la ruta decida el flujo.
    """
    payload, error, status = delete_json(f"/articulos/{articulo_id}", token=token)
    if error:
        return False, error, status
    return True, None, status
