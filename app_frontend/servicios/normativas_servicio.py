from servicios.api_client import get_json, post_json, put_json, delete_json

TIMEOUT = 5


def obtener_normativas():
    """Obtiene la lista de normativas desde el backend. Devuelve [] en caso de error."""
    payload, error = get_json("/normativas")
    if error:
        return []
    return payload or []


def crear_normativa(data):
    """Crea una nueva normativa en el backend. Devuelve el objeto creado o {} en caso de fallo."""
    payload, error, status = post_json("/normativas", data)
    if error:
        return {}
    return payload or {}


def actualizar_normativa(id_normativa, data):
    """Actualiza una normativa existente. Devuelve el objeto actualizado o {} en caso de fallo."""
    payload, error, status = put_json(f"/normativas/{id_normativa}", data)
    if error:
        return {}
    return payload or {}


def eliminar_normativa(id_normativa):
    """Elimina una normativa y devuelve True en caso de éxito."""
    payload, error, status = delete_json(f"/normativas/{id_normativa}")
    if error:
        return False
    return True
