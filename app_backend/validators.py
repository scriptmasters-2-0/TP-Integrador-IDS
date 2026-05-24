

def valid_user(data):
    if not isinstance(data, dict):
        return False, "payload_must_be_object"
    required = ["username", "email", "password", "firstName", "lastName", "career"]
    for f in required:
        v = data.get(f)
        if v is None:
            return False, f"missing:{f}"
        if isinstance(v, str) and v.strip() == "":
            return False, f"empty:{f}"
    username = data.get("username")
    if not isinstance(username, str) or len(username.strip()) < 3:
        return False, "invalid:username"
    email = data.get("email")
    if not isinstance(email, str) or "@" not in email or "." not in email.split("@")[-1]:
        return False, "invalid:email"
    password = data.get("password")
    if not isinstance(password, str) or len(password) < 6:
        return False, "invalid:password"
    role = data.get("role")
    allowed = ["alumno", "docente", "bibliotecario", "admin"]
    if role not in allowed and role is not None:
        return False, "invalid:role"
    career = data.get("career")
    if career is not None and not isinstance(career, str):
        return False, "invalid:career"
    return True, None
