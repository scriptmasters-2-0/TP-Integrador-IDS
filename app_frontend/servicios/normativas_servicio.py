from servicios.api_client import get_json, post_json, put_json, delete_json
from servicios.paginacion_servicio import extraer_data_paginada


def obtener_normativas(params=None):
    """Obtiene la lista de normativas desde el backend. Devuelve [] en caso de error."""
    payload, error = get_json("/normativas", params=params)
    if error:
        return []
    return extraer_data_paginada(payload)


def obtener_normativas_paginadas(params=None):
    """Obtiene normativas preservando metadata y links HATEOAS."""
    payload, error = get_json("/normativas", params=params)
    if error:
        return {"data": [], "pagination": {}, "links": {}}, error
    return payload or {"data": [], "pagination": {}, "links": {}}, None


def crear_normativa(data, token=None):
    """Crea una normativa y devuelve (payload, error, status)."""
    return post_json("/normativas", data, token=token)


def actualizar_normativa(id_normativa, data, token=None):
    """Actualiza una normativa y devuelve (payload, error, status)."""
    return put_json(f"/normativas/{id_normativa}", data, token=token)


def eliminar_normativa(id_normativa, token=None):
    """Elimina una normativa y devuelve (ok, error, status)."""
    payload, error, status = delete_json(f"/normativas/{id_normativa}", token=token)
    if error:
        return False, error, status
    return True, None, status
