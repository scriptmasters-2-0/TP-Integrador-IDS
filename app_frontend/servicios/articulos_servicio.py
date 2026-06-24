from servicios.api_client import get_json, post_json, put_json, delete_json
from servicios.paginacion_servicio import extraer_data_paginada

TIPOS_ARTICULO_RESPALDO = [
    {"valor": "Libro", "etiqueta": "Libros"},
    {"valor": "Electronicos", "etiqueta": "Equipos Electrónicos"},
    {"valor": "Herramienta", "etiqueta": "Herramientas"},
    {"valor": "Proyector", "etiqueta": "Proyectores"},
    {"valor": "Accesorios", "etiqueta": "Accesorios y Cables"},
]

SECCIONES_ARTICULO_RESPALDO = [
    {"valor": "Biblioteca", "etiqueta": "Biblioteca"},
    {"valor": "Tecnologia", "etiqueta": "Tecnología"},
    {"valor": "Bedelia", "etiqueta": "Bedelía"},
    {"valor": "Laboratorio", "etiqueta": "Laboratorio"},
    {"valor": "Otros", "etiqueta": "Otros"},
]

OPCIONES_ARTICULO_RESPALDO = {
    "tipos": TIPOS_ARTICULO_RESPALDO,
    "secciones": SECCIONES_ARTICULO_RESPALDO,
}

ICONOS_TIPO_ARTICULO = {
    "Libro": "fa-book",
    "Electronicos": "fa-laptop",
    "Proyector": "fa-display",
    "Accesorios": "fa-plug",
    "Herramienta": "fa-screwdriver-wrench",
}


def obtener_opciones_articulo():
    """GET /articulos/opciones con respaldo local para renderizar formularios."""
    payload, error = get_json("/articulos/opciones")
    if error or not isinstance(payload, dict):
        return OPCIONES_ARTICULO_RESPALDO
    if not isinstance(payload.get("tipos"), list) or not isinstance(
        payload.get("secciones"), list
    ):
        return OPCIONES_ARTICULO_RESPALDO
    return payload


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
