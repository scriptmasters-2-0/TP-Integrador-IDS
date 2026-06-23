"""Validadores de datos de entrada para las solicitudes de la API.

Contiene funciones de validación para los payloads de creación,
actualización y filtrado de usuarios, ítems, préstamos y penalidades.
"""

MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 8


def valid_id(value):
    """Valida identificadores enteros positivos.

    Args:
        value: Valor a validar como identificador.

    Returns:
        int: El valor convertido a entero si es válido, o None en caso contrario.

    """
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        val = int(value)
    except (ValueError, TypeError):
        return None

    if val <= 0:
        return None

    return val


def valid_usuario(data):
    """Valida el payload de creación de usuario.

    Verifica que los campos requeridos (nombre, email, carrera) estén
    presentes y que los campos opcionales tengan valores válidos.

    Args:
        data (dict): Diccionario con los datos del usuario a crear.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    allowed_fields = ["nombre", "email", "rol", "carrera", "contrasenia"]
    for f in data:
        if f not in allowed_fields:
            return False, f"invalid_field:{f}"

    required = ["nombre", "email", "carrera"]
    for f in required:
        v = data.get(f)
        if v is None:
            return False, f"missing:{f}"
        if isinstance(v, str) and v.strip() == "":
            return False, f"empty:{f}"

    email = data.get("email")
    if not isinstance(email, str) or not email.endswith("@fi.uba.ar"):
        return False, "invalid:email"

    rol = data.get("rol")
    allowed = ["alumno", "profesor", "bibliotecario", "admin"]
    if rol not in allowed and rol is not None:
        return False, "invalid:rol"

    carrera = data.get("carrera")
    if carrera is not None and not isinstance(carrera, str):
        return False, "invalid:carrera"

    return True, None


def valid_contrasenia(value):
    """Valida una contraseña para creación o cambio de usuario."""
    if value is None:
        return False, "missing:contrasenia"
    if not isinstance(value, str):
        return False, "invalid_type:contrasenia"
    if value.strip() == "":
        return False, "empty:contrasenia"
    if len(value) < MIN_PASSWORD_LENGTH:
        return False, "invalid_length:contrasenia"

    return True, None


def valid_usuario_update(data):
    """Valida el payload de actualización de usuario.

    Verifica que al menos un campo actualizable esté presente y que
    los valores proporcionados sean válidos.

    Args:
        data (dict): Diccionario con los campos a actualizar.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    allowed = ["nombre", "email", "rol", "carrera", "activo"]
    for key in data:
        if key not in allowed:
            return False, f"invalid_field:{key}"

    if not any(k in data for k in allowed):
        return False, "no_updatable_fields"

    if "nombre" in data:
        if data["nombre"] is None:
            return False, "null:nombre"
        if not isinstance(data["nombre"], str):
            return False, "invalid_type:nombre"
        if data["nombre"].strip() == "":
            return False, "empty:nombre"

    if "email" in data:
        if data["email"] is None:
            return False, "null:email"
        if not isinstance(data["email"], str):
            return False, "invalid_type:email"
        if data["email"].strip() == "":
            return False, "empty:email"
        if not data["email"].endswith("@fi.uba.ar"):
            return False, "invalid_format:email"

    if "rol" in data:
        if data["rol"] is None:
            return False, "null:rol"
        if not isinstance(data["rol"], str):
            return False, "invalid_type:rol"
        if data["rol"].strip() == "":
            return False, "empty:rol"
        allowed_roles = ["alumno", "profesor", "bibliotecario", "admin"]
        if data["rol"] not in allowed_roles:
            return False, "invalid_value:rol"

    if "activo" in data:
        if data["activo"] is None:
            return False, "null:activo"
        if data["activo"] not in (True, False, 0, 1, "0", "1"):
            return False, "invalid_value:activo"

    if "carrera" in data:
        if data.get("carrera") is None:
            return False, "null:carrera"
        if not isinstance(data.get("carrera"), str):
            return False, "invalid_type:carrera"
        if data.get("carrera").strip() == "":
            return False, "empty:carrera"

    return True, None


def valid_login(data):
    """Valida el payload de inicio de sesión.

    Verifica que los campos email y contrasenia estén presentes,
    sean cadenas no vacías y que email tenga formato básico válido.

    Args:
        data (dict): Diccionario con las credenciales de inicio de sesión.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    if data.get("email") is None:
        return False, "missing:email"
    if not isinstance(data.get("email"), str):
        return False, "invalid_type:email"
    if data.get("email").strip() == "":
        return False, "empty:email"
    email = data.get("email").strip()
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "invalid_value:email"

    if data.get("contrasenia") is None:
        return False, "missing:contrasenia"
    if not isinstance(data.get("contrasenia"), str):
        return False, "invalid_type:contrasenia"
    if data.get("contrasenia").strip() == "":
        return False, "empty:contrasenia"

    return True, None


def _valid_required_string(data, field):
    """Valida que un campo de texto requerido esté presente y no vacío.

    Args:
        data (dict): Diccionario con los datos a validar.
        field (str): Nombre del campo a verificar.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    value = data.get(field)
    if value is None:
        return False, f"missing:{field}"
    if not isinstance(value, str):
        return False, f"invalid_type:{field}"
    if value.strip() == "":
        return False, f"empty:{field}"

    return True, None


def _valid_optional_string(data, field):
    """Valida que un campo de texto opcional, si está presente, sea válido.

    Si el campo no está presente en el diccionario, se considera válido.
    Si está presente, debe ser una cadena no nula y no vacía.

    Args:
        data (dict): Diccionario con los datos a validar.
        field (str): Nombre del campo a verificar.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if field not in data:
        return True, None
    if data.get(field) is None:
        return False, f"null:{field}"
    if not isinstance(data.get(field), str):
        return False, f"invalid_type:{field}"
    if data.get(field).strip() == "":
        return False, f"empty:{field}"

    return True, None


def _valid_optional_positive_int(data, field):
    """Valida que un campo entero positivo opcional, si está presente, sea válido.

    Si el campo no está presente en el diccionario, se considera válido.
    Si está presente, debe ser un entero estrictamente mayor que cero.

    Args:
        data (dict): Diccionario con los datos a validar.
        field (str): Nombre del campo a verificar.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if field not in data:
        return True, None
    if data.get(field) is None:
        return False, f"null:{field}"
    try:
        value = int(data.get(field))
    except (ValueError, TypeError):
        return False, f"invalid_type:{field}"
    if value <= 0:
        return False, f"invalid_value:{field}"

    return True, None


def _valid_optional_non_negative_int(data, field):
    """Valida que un campo entero no negativo opcional, si está presente, sea válido.

    Si el campo no está presente en el diccionario, se considera válido.
    Si está presente, debe ser un entero mayor o igual a cero.

    Args:
        data (dict): Diccionario con los datos a validar.
        field (str): Nombre del campo a verificar.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if field not in data:
        return True, None
    if data.get(field) is None:
        return False, f"null:{field}"
    try:
        value = int(data.get(field))
    except (ValueError, TypeError):
        return False, f"invalid_type:{field}"
    if value < 0:
        return False, f"invalid_value:{field}"

    return True, None


def _valid_optional_bool(data, field):
    """Valida que un campo booleano opcional, si está presente, sea válido.

    Si el campo no está presente en el diccionario, se considera válido.
    Si está presente, debe ser de tipo booleano.

    Args:
        data (dict): Diccionario con los datos a validar.
        field (str): Nombre del campo a verificar.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if field not in data:
        return True, None
    if not isinstance(data.get(field), bool):
        return False, f"invalid_type:{field}"

    return True, None


def valid_articulo(data):
    """Valida el payload de creación de un ítem.

    Verifica que los campos requeridos (nombre_art, tipo, seccion,
    prestacion_maxima) estén presentes y que los opcionales (stock,
    necesita_reparacion) tengan valores válidos.

    Args:
        data (dict): Diccionario con los datos del ítem a crear.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    for field in ("nombre_art", "tipo", "seccion"):
        is_valid, error = _valid_required_string(data, field)
        if not is_valid:
            return False, error

    if data.get("prestacion_maxima") is None:
        return False, "missing:prestacion_maxima"

    is_valid, error = _valid_optional_positive_int(data, "prestacion_maxima")
    if not is_valid:
        return False, error

    is_valid, error = _valid_optional_non_negative_int(data, "stock")
    if not is_valid:
        return False, error

    is_valid, error = _valid_optional_bool(data, "necesita_reparacion")
    if not is_valid:
        return False, error

    return True, None


def valid_articulo_update(data):
    """Valida el payload de actualización de un ítem.

    Verifica que al menos un campo actualizable esté presente,
    que no haya campos no permitidos y que los valores sean válidos.

    Args:
        data (dict): Diccionario con los campos a actualizar.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    allowed = [
        "nombre_art",
        "tipo",
        "seccion",
        "prestacion_maxima",
        "stock",
        "necesita_reparacion",
        "activo",
    ]

    if not any(k in data for k in allowed):
        return False, "no_updatable_fields"

    invalid_fields = [field for field in data if field not in allowed]
    if invalid_fields:
        return False, f"invalid_fields:{','.join(invalid_fields)}"

    for field in ("nombre_art", "tipo", "seccion"):
        is_valid, error = _valid_optional_string(data, field)
        if not is_valid:
            return False, error

    is_valid, error = _valid_optional_positive_int(data, "prestacion_maxima")
    if not is_valid:
        return False, error

    is_valid, error = _valid_optional_non_negative_int(data, "stock")
    if not is_valid:
        return False, error

    is_valid, error = _valid_optional_bool(data, "necesita_reparacion")
    if not is_valid:
        return False, error

    is_valid, error = _valid_optional_bool(data, "activo")
    if not is_valid:
        return False, error

    return True, None


def valid_articulo_filters(filters):
    """Valida y parsea los filtros de consulta de ítems.

    Procesa los filtros de tipo, sección, disponibilidad y
    necesidad de reparación proporcionados como query parameters.

    Args:
        filters: Objeto con los parámetros de consulta a validar.

    Returns:
        tuple: (True, None, dict) con los filtros parseados si son válidos,
            o (False, str, None) con mensaje de error si no lo son.

    """
    parsed_filters = {
        "tipo": None,
        "seccion": None,
        "disponible": None,
        "necesita_reparacion": None,
    }

    for field in ("tipo", "seccion"):
        value = filters.get(field)
        if value is not None:
            if value.strip() == "":
                return False, f"empty:{field}", None
            parsed_filters[field] = value

    for field in ("disponible", "necesita_reparacion"):
        value = filters.get(field)
        if value is not None:
            normalized = value.lower()
            if normalized in ("true", "1"):
                parsed_filters[field] = True
            elif normalized in ("false", "0"):
                parsed_filters[field] = False
            else:
                return False, f"invalid_value:{field}", None

    return True, None, parsed_filters


def valid_penalty_patch(data):
    """Valida el payload de actualización parcial de una penalidad.

    Verifica que al menos un campo actualizable (status, severidad, notes)
    esté presente y que los valores proporcionados sean válidos.

    Args:
        data (dict): Diccionario con los campos a actualizar.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    allowed = ["status", "severidad", "notes"]
    if not any(k in data for k in allowed):
        return False, "no_updatable_fields"

    if "status" in data:
        if data.get("status") is None:
            return False, "null:status"
        if not isinstance(data.get("status"), str):
            return False, "invalid_type:status tiene que ser un string"
        if data.get("status") not in ("Activa", "Levantada"):
            return False, "invalid_type:status tiene que ser 'Activa' o 'Levantada'"

    if "severidad" in data:
        if data.get("severidad") is None:
            return False, "null:severidad"
        if not isinstance(data.get("severidad"), str):
            return False, "invalid_type:severidad"
        if data.get("severidad").strip() == "":
            return False, "empty:severidad"

    if "notes" in data:
        if data.get("notes") is None:
            return False, "null:notes"
        if not isinstance(data.get("notes"), str):
            return False, "invalid_type:notes"
        if data.get("notes").strip() == "":
            return False, "empty:notes"

    return True, None


def valid_reserva_status_update(data):
    """Valida el payload de actualización de estado de un préstamo.

    Verifica que el campo estado_reserva esté presente, sea una cadena
    y contenga uno de los estados permitidos.

    Args:
        data (dict): Diccionario con el nuevo estado del préstamo.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    if data.get("estado_reserva") is None:
        return False, "missing:estado_reserva"
    if not isinstance(data.get("estado_reserva"), str):
        return False, "invalid_type:estado_reserva"

    allowed_statuses = (
        "pendiente",
        "aprobado",
        "entregado",
        "devuelto",
        "cancelado",
        "rechazado",
    )
    if data.get("estado_reserva") not in allowed_statuses:
        return False, "invalid_value:estado_reserva"

    if "estado_devuelto" in data and data.get("estado_devuelto") is not None:
        if not isinstance(data.get("estado_devuelto"), str):
            return False, "invalid_type:estado_devuelto"

        allowed_return_conditions = ("bueno", "danado", "perdido")
        if data.get("estado_reserva") == "devuelto":
            if data.get("estado_devuelto") not in allowed_return_conditions:
                return False, "invalid_value:estado_devuelto"
        elif data.get("estado_devuelto") not in (*allowed_return_conditions, "no_aplica"):
            return False, "invalid_value:estado_devuelto"

    return True, None


def valid_reserva_create(data):
    """Valida el payload de creación de préstamo.

    Verifica que los campos usuario_id e articulo_id estén presentes
    y que sean identificadores enteros positivos.

    Args:
        data (dict): Diccionario con los campos del préstamo a crear.

    Returns:
        tuple: (True, None, dict) con valores parseados si es válido,
            o (False, str, None) con detalle del error.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object", None

    if data.get("usuario_id") is None:
        return False, "missing:usuario_id", None
    if data.get("articulo_id") is None:
        return False, "missing:articulo_id", None

    usuario_id = valid_id(data.get("usuario_id"))
    if usuario_id is None:
        return False, "invalid_value:usuario_id", None

    articulo_id = valid_id(data.get("articulo_id"))
    if articulo_id is None:
        return False, "invalid_value:articulo_id", None

    parsed = {"usuario_id": usuario_id, "articulo_id": articulo_id}

    has_fecha_retiro = "fecha_retiro" in data
    has_hora_regreso = "hora_regreso" in data
    if has_fecha_retiro and not has_hora_regreso:
        return False, "missing:hora_regreso", None
    if has_hora_regreso and not has_fecha_retiro:
        return False, "missing:fecha_retiro", None

    for field in ("fecha_retiro", "hora_regreso"):
        if field not in data:
            continue
        value = data.get(field)
        if value is None:
            return False, f"null:{field}", None
        if not isinstance(value, str):
            return False, f"invalid_type:{field}", None
        value = value.strip()
        if value == "":
            return False, f"empty:{field}", None
        parsed[field] = value

    return True, None, parsed


def valid_usuario_id_query(filters):
    """Valida y parsea query params que requieren usuario_id.

    Args:
        filters: Objeto con query params (por ejemplo request.args).

    Returns:
        tuple: (True, None, int) con usuario_id parseado si es válido,
            o (False, str, None) con detalle del error.

    """
    if filters is None:
        return False, "missing:usuario_id", None

    raw_usuario_id = filters.get("usuario_id")
    if raw_usuario_id is None:
        return False, "missing:usuario_id", None

    usuario_id = valid_id(raw_usuario_id)
    if usuario_id is None:
        return False, "invalid_value:usuario_id", None

    return True, None, usuario_id
