"""Funciones de servicio para consumir los endpoints de /api/usuarios.

Actúa como capa intermedia entre las vistas del frontend y la API backend,
encapsulando las llamadas HTTP y el manejo de errores.
"""

from servicios.api_client import get_json, post_json, put_json, delete_json, patch_json
from servicios.paginacion_servicio import extraer_data_paginada

TIMEOUT = 5


def obtener_usuarios(params=None, token=None):
    """Obtiene la lista de usuarios desde la API.

    devuelve la respuesta cruda sin procesar el envelope HATEOAS. Si el backend ya migró al contrato
    HATEOAS, el payload devuelto será un dict con 'data'. Para vistas
    paginadas usar obtener_usuarios_paginados().

    Args:
        params (dict | None): Parámetros de consulta opcionales, por ejemplo
            {'usuario': 'Juan', 'limit': 10, 'offset': 0}.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        list | dict: Payload de la respuesta en caso de éxito,
            lista vacía en caso de error.

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
    """Crea un nuevo usuario en la API.

    Args:
        usuario_data (dict): Datos del usuario a crear. Debe incluir:
            - nombre (str): Nombre completo del usuario.
            - email (str): Correo electrónico único.
            - rol (str): Rol del usuario ('admin', 'bibliotecario',
              'profesor' o 'alumno').
            - carrera (str): Carrera del usuario.
            - puntaje (int): Opcional, por defecto 0.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        dict: JSON del usuario creado en caso de éxito,
            diccionario vacío en caso de error.

    """
    return post_json("/usuarios", usuario_data, token=token)


def obtener_usuario(usuario_id, token=None):
    """Obtiene un usuario por su identificador.

    Args:
        usuario_id (int): Identificador único del usuario a consultar.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        dict: JSON del usuario en caso de éxito,
            diccionario vacío si no existe o en caso de error.

    """
    payload, error = get_json(f"/usuarios/{usuario_id}", token=token)
    if error:
        return {}
    return payload or {}


def actualizar_usuario(usuario_id, usuario_data, token=None):
    """Actualiza los datos de un usuario existente.

    Args:
        usuario_id (int): Identificador del usuario a actualizar.
        usuario_data (dict): Campos a actualizar. Puede incluir nombre,
            email, rol, carrera, puntaje u otros campos del usuario.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        dict: JSON del usuario actualizado en caso de éxito,
            diccionario vacío en caso de error.

    """
    return put_json(f"/usuarios/{usuario_id}", usuario_data, token=token)


def eliminar_usuario(usuario_id, token=None):
    """Da de baja lógica a un usuario.

    El usuario no se elimina físicamente sino que se marca como inactivo en la base de datos.
    Requiere rol admin.

    Args:
        usuario_id (int): Identificador del usuario a dar de baja.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        bool: True en caso de éxito,
            diccionario vacío en caso de error.

    """
    payload, error, status = delete_json(f"/usuarios/{usuario_id}", token=token)
    if error:
        return False, error, status
    return True, None, status


def establecer_estado_usuario(usuario_id, status_data, token=None):
    """Actualiza el estado activo/inactivo de un usuario.

    Args:
        usuario_id (int): Identificador del usuario a modificar.
        status_data (dict): Datos del nuevo estado, por ejemplo
            {'active': True} o {'active': False}.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        bool: True en caso de éxito,
            diccionario vacío en caso de error.

    """
    payload, error, status = patch_json(f"/usuarios/{usuario_id}/status", status_data, token=token)
    if error:
        return {}
    return True


def obtener_reservas_usuario(usuario_id, params=None, token=None):
    """Obtiene la lista de reservas de un usuario específico.
    Alumnos y profesores solo pueden consultar sus propias reservas; admins y bibliotecarios pueden
    consultar las de cualquier usuario.

    Args:
        usuario_id (int): Identificador del usuario cuyas reservas se consultan.
        params (dict | None): Parámetros de consulta opcionales.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        list: Lista de reservas del usuario en caso de éxito,
            lista vacía en caso de error.

    """
    payload, error = get_json(f"/usuarios/{usuario_id}/reservas", token=token, params=params)
    if error:
        return []
    return payload or []


def obtener_reservas_usuario_con_error(usuario_id, params=None, token=None):
    """Obtiene las reservas de un usuario preservando el mensaje de error.

    Variante de obtener_reservas_usuario() que expone el error al
    llamador en lugar de silenciarlo, útil para mostrar mensajes
    específicos en las vistas.

    Args:
        usuario_id (int): Identificador del usuario cuyas reservas se consultan.
        params (dict | None): Parámetros de consulta opcionales.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        tuple[list, str | None]: Par (lista de reservas, mensaje de error).
            El error es None si la operación fue exitosa.

    """
    payload, error = get_json(f"/usuarios/{usuario_id}/reservas", token=token, params=params)
    if error:
        return [], error
    return payload or [], None


def obtener_penalizaciones_usuario(usuario_id, params=None, token=None):
    """Obtiene la lista de penalizaciones de un usuario específico.
    Args:
        usuario_id (int): Identificador del usuario cuyas penalizaciones
            se desean consultar.
        params (dict | None): Parámetros de consulta opcionales.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        list: Lista de penalizaciones del usuario en caso de éxito,
            lista vacía en caso de error.

    """
    payload, error = get_json(f"/usuarios/{usuario_id}/penalizaciones", token=token, params=params)
    if error:
        return []
    return payload or []


def obtener_usuarios_paginados(params=None, token=None):
    """Obtiene el listado paginado de usuarios en formato HATEOAS.

    Realiza GET /api/usuarios y adapta la respuesta al formato esperado
    por los templates del frontend, separando datos, metadata de
    paginación y links navegables.

    Args:
        params (dict | None): Parámetros de consulta opcionales, por ejemplo
            {'limit': 10, 'offset': 0, 'usuario': 'Juan'}.
        token (str | None): JWT de autenticación. Si no se pasa, se
            intenta obtener desde la sesión Flask.

    Returns:
        dict: Diccionario con las claves:
            - datos (list): Lista de usuarios de la página actual.
            - pagination (dict): Metadata con limit, offset, total y count.
            - links (dict): Enlaces HATEOAS first, prev, next, last.
            Retorna diccionario vacío en caso de error.

    """
    payload, error = get_json("/usuarios", token=token, params=params)
    if error:
        return {}
    if not isinstance(payload, dict):
        return {}

    return {
        "datos": extraer_data_paginada(payload),
        "pagination": payload.get("pagination") or {},
        "links": payload.get("links") or {},
    }