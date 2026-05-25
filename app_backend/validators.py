"""Request payload validators."""

MIN_USERNAME_LENGTH = 3


def valid_id(value):
    """Validate positive integer identifiers."""
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
    """Validate user creation payload."""
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
    """Validate user update payload."""
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
    """Validate login payload."""
    if not isinstance(data, dict):
        return False, "payload_must_be_object"

    if data.get("username") is None:
        return False, "missing:username"
    if not isinstance(data.get("username"), str):
        return False, "invalid_type:username"
    if data.get("username").strip() == "":
        return False, "empty:username"
    if len(data.get("username").strip()) < MIN_USERNAME_LENGTH:
        return False, "invalid_value:username"

    if data.get("password") is None:
        return False, "missing:password"
    if not isinstance(data.get("password"), str):
        return False, "invalid_type:password"
    if data.get("password").strip() == "":
        return False, "empty:password"

    return True, None


def _valid_required_string(data, field):
    value = data.get(field)
    if value is None:
        return False, f"missing:{field}"
    if not isinstance(value, str):
        return False, f"invalid_type:{field}"
    if value.strip() == "":
        return False, f"empty:{field}"

    return True, None


def _valid_optional_string(data, field):
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
    if field not in data:
        return True, None
    if not isinstance(data.get(field), bool):
        return False, f"invalid_type:{field}"

    return True, None


def valid_item(data):  # noqa: PLR0911
    """Validate item creation payload."""
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
    """Validate item update payload."""
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
    """Validate and parse item query filters."""
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
    """Validate penalty partial update payload."""
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
