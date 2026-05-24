

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
