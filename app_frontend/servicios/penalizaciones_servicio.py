"""Funciones de servicio para consumir los endpoints de /api/penalizaciones.

Actúa como capa intermedia entre las vistas del frontend y la API backend,
encapsulando las llamadas HTTP y el manejo de errores.
"""

from servicios.api_client import get_json, post_json, put_json, patch_json
from servicios.paginacion_servicio import extraer_data_paginada

TIMEOUT = 5


def obtener_penalizaciones(params=None, token=None):
    """Obtiene la lista de penalizaciones desde la API.
    Args:
        params (dict | None): Parámetros de consulta opcionales, por ejemplo
            {'usuario_id': 5, 'limit': 10, 'offset': 0}.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        list | dict: Payload de la respuesta en caso de éxito,
            lista vacía en caso de error.

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
    """Crea una nueva penalización en la API.
    Args:
        penalty_data (dict): Datos de la penalización. Debe incluir:
            - usuario_id (int): Identificador del usuario a penalizar.
            - reason (str): Motivo de la penalización.
            - severidad (str): Opcional. 'baja', 'media' o 'alta'.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        dict: JSON de la penalización creada en caso de éxito,
            diccionario vacío en caso de error.

    """
    payload, error, status = post_json("/penalizaciones", penalty_data, token=token)
    if error:
        return {}
    return payload or {}


def obtener_penalizacion(penalty_id, token=None):
    """Obtiene una penalización por su identificador.
    Args:
        penalty_id (int): Identificador de la penalización a consultar.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        dict: JSON de la penalización en caso de éxito,
            diccionario vacío en caso de error o no encontrado.

    """
    payload, error = get_json(f"/penalizaciones/{penalty_id}", token=token)
    if error:
        return {}
    return payload or {}


def actualizar_penalizacion(penalty_id, penalty_data, token=None):
    """Actualiza completamente una penalización existente.
    Args:
        penalty_id (int): Identificador de la penalización a actualizar.
        penalty_data (dict): Datos completos de la penalización a reemplazar.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        dict: JSON actualizado en caso de éxito,
            diccionario vacío en caso de error.

    """
    payload, error, status = put_json(f"/penalizaciones/{penalty_id}", penalty_data, token=token)
    if error:
        return {}
    return payload or {}


def actualizar_parcial_penalizacion(penalty_id, patch_data, token=None):
    """Actualiza parcialmente una penalización existente.
    Args:
        penalty_id (int): Identificador de la penalización a modificar.
        patch_data (dict): Campos a actualizar. Puede incluir:
            - status (str): 'Activa' o 'Levantada'.
            - notes (str): Notas o motivo actualizado.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        bool: True en caso de éxito,
            diccionario vacío en caso de error.

    """
    payload, error, status = patch_json(f"/penalizaciones/{penalty_id}", patch_data, token=token)
    if error:
        return {}
    return True


def obtener_penalizaciones_paginadas(params=None, token=None):
    """Obtiene el listado paginado de penalizaciones en formato HATEOAS.
    Args:
        params (dict | None): Parámetros de consulta opcionales, por ejemplo
            {'limit': 10, 'offset': 0, 'usuario_id': 3, 'usuario': 'Juan'}.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        dict: Diccionario con las claves:
            - datos (list): Lista de penalizaciones de la página actual.
            - pagination (dict): Metadata con limit, offset, total y count.
            - links (dict): Enlaces HATEOAS first, prev, next, last.
            Retorna diccionario vacío en caso de error.

    """
    payload, error = get_json("/penalizaciones", token=token, params=params)
    if error:
        return {}
    if not isinstance(payload, dict):
        return {}

    return {
        "datos": extraer_data_paginada(payload),
        "pagination": payload.get("pagination") or {},
        "links": payload.get("links") or {},
    }
