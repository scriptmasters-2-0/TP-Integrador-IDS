"""Validadores de datos de entrada para las solicitudes de la API.

Contiene funciones de validación para los payloads de creación,
actualización y filtrado de usuarios, ítems, préstamos y penalidades.
"""

MIN_USERNAME_LENGTH = 3


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


def valid_user(data):  # noqa: PLR0911
    """Valida el payload de creación de usuario.

    Verifica que los campos requeridos (nombre, mail, carrera) estén
    presentes y que los campos opcionales (rol, score) tengan valores válidos.

    Args:
        data (dict): Diccionario con los datos del usuario a crear.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    required = ["nombre", "mail", "carrera"]
    for f in required:
        v = data.get(f)
        if v is None:
            return False, f"missing:{f}"
        if isinstance(v, str) and v.strip() == "":
            return False, f"empty:{f}"

    mail = data.get("mail")
    if not isinstance(mail, str) or "@" not in mail or "." not in mail.split("@")[-1]:
        return False, "invalid:mail"

    rol = data.get("rol")
    allowed = ["alumno", "docente", "bibliotecario", "admin"]
    if rol not in allowed and rol is not None:
        return False, "invalid:rol"

    score = data.get("score")
    if score is not None:
        try:
            s = int(score)
            if s < 0:
                return False, "invalid:score"
        except (ValueError, TypeError):
            return False, "invalid:score"

    carrera = data.get("carrera")
    if carrera is not None and not isinstance(carrera, str):
        return False, "invalid:carrera"

    return True, None


def valid_user_update(data):  # noqa: PLR0911, PLR0912
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

    allowed = ["nombre", "mail", "rol", "carrera", "score"]
    if not any(k in data for k in allowed):
        return False, "no_updatable_fields"

    if "nombre" in data:
        if data["nombre"] is None:
            return False, "null:nombre"
        if not isinstance(data["nombre"], str):
            return False, "invalid_type:nombre"
        if data["nombre"].strip() == "":
            return False, "empty:nombre"

    if "mail" in data:
        if data["mail"] is None:
            return False, "null:mail"
        if not isinstance(data["mail"], str):
            return False, "invalid_type:mail"
        if data["mail"].strip() == "":
            return False, "empty:mail"
        if "@" not in data["mail"] or "." not in data["mail"].split("@")[-1]:
            return False, "invalid_format:mail"

    if "rol" in data:
        if data["rol"] is None:
            return False, "null:rol"
        if not isinstance(data["rol"], str):
            return False, "invalid_type:rol"
        if data["rol"].strip() == "":
            return False, "empty:rol"
        allowed_roles = ["alumno", "docente", "bibliotecario", "admin"]
        if data["rol"] not in allowed_roles:
            return False, "invalid_value:rol"

    if "score" in data:
        if data["score"] is None:
            return False, "null:score"
        try:
            s = int(data["score"])
        except (ValueError, TypeError):
            return False, "invalid_type:score"
        if s < 0:
            return False, "invalid_value:score"

    if "carrera" in data:
        if data.get("carrera") is None:
            return False, "null:carrera"
        if not isinstance(data.get("carrera"), str):
            return False, "invalid_type:carrera"
        if data.get("carrera").strip() == "":
            return False, "empty:carrera"

    return True, None


def valid_login(data):  # noqa: PLR0911
    """Valida el payload de inicio de sesión.

    Verifica que los campos email y password estén presentes,
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

    if data.get("password") is None:
        return False, "missing:password"
    if not isinstance(data.get("password"), str):
        return False, "invalid_type:password"
    if data.get("password").strip() == "":
        return False, "empty:password"

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


def valid_item(data):  # noqa: PLR0911
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


def valid_item_update(data):  # noqa: PLR0911
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

    return True, None


def valid_item_filters(filters):
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


def valid_penalty_patch(data):  # noqa: PLR0911, PLR0912
    """Valida el payload de actualización parcial de una penalidad.

    Verifica que al menos un campo actualizable (status, severity, notes)
    esté presente y que los valores proporcionados sean válidos.

    Args:
        data (dict): Diccionario con los campos a actualizar.

    Returns:
        tuple: (True, None) si es válido, (False, str) con mensaje de error
            si no lo es.

    """
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    allowed = ["status", "severity", "notes"]
    if not any(k in data for k in allowed):
        return False, "no_updatable_fields"

    if "status" in data:
        if data.get("status") is None:
            return False, "null:status"
        if not isinstance(data.get("status"), str):
            return False, "invalid_type:status"
        if data.get("status") not in ("Activa", "Levantada"):
            return False, "invalid_value:status"

    if "severity" in data:
        if data.get("severity") is None:
            return False, "null:severity"
        if not isinstance(data.get("severity"), str):
            return False, "invalid_type:severity"
        if data.get("severity").strip() == "":
            return False, "empty:severity"

    if "notes" in data:
        if data.get("notes") is None:
            return False, "null:notes"
        if not isinstance(data.get("notes"), str):
            return False, "invalid_type:notes"
        if data.get("notes").strip() == "":
            return False, "empty:notes"

    return True, None


def valid_loan_status_update(data):
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

    allowed_statuses = ("pendiente", "aprobado", "entregado", "devuelto", "cancelado")
    if data.get("estado_reserva") not in allowed_statuses:
        return False, "invalid_value:estado_reserva"

    return True, None
