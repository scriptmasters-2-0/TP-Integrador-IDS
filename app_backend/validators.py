

def valid_id(value):
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


def valid_user(data):
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


def valid_user_update(data):
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
        if data["carrera"] is None:
            return False, "null:carrera"
        if not isinstance(data["carrera"], str):
            return False, "invalid_type:carrera"
        if data["carrera"].strip() == "":
            return False, "empty:carrera"

    return True, None
