import bcrypt
import jwt
from flask import Blueprint, jsonify, request

from config import JWT_ALGORITHM, JWT_SECRET
from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    MSG_BAD_REQUEST,
    MSG_DB_CONNECTION_FAILED,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_UNAUTHORIZED,
)
from validators import valid_login

auth_bp = Blueprint("auth", __name__)


def hashear_password(password):
    hash_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    return hash_bytes.decode("utf-8")


def valid_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    except (ValueError, TypeError):
        return False


def generar_token(user_id, rol):
    payload = {
        "user_id": user_id,
        "rol": rol,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]), "Valid"

    except jwt.ExpiredSignatureError:
        return None, "Expired"

    except jwt.InvalidTokenError:
        return None, "Invalid"


def extraer_token_del_header():
    header = request.headers.get("Authorization", "")

    if not header.startswith("Bearer "):
        return None, "Incorrect token type"

    return header[len("Bearer ") :].strip(), "Ok"


def requiere_auth(rol):
    def wrapperGenerator(route):

        def wrapper(*args, **kwargs):
            token, tokenError = extraer_token_del_header()

            if token is None:
                return jsonify({"error": tokenError}), HTTP_UNAUTHORIZED

            payload, payloadError = decodificar_token(token)

            if payload is None:
                return jsonify({"error": payloadError}), HTTP_UNAUTHORIZED

            if payload.get("rol") != rol:
                return jsonify({"error": MSG_UNAUTHORIZED}), HTTP_UNAUTHORIZED

            return route(*args, **kwargs)

        return wrapper

    return wrapperGenerator


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():

    try:
        data = request.get_json()

    except Exception:
        data = None

    is_valid, error = valid_login(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    username = data.get("username")
    password = data.get("password")

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        sql_query = "SELECT id, nombre, mail, score, rol, carrera, password_hash FROM usuario WHERE nombre = %(value)s LIMIT 1"
        value = {"value": username}

        cursor.execute(sql_query, value)

        user = cursor.fetchone()
        if not user:
            return (
                jsonify({"error": MSG_UNAUTHORIZED, "detail": "invalid_credentials"}),
                HTTP_UNAUTHORIZED,
            )

        password_hash = user.get("password_hash", "")

        if not valid_password(password, password_hash) and password_hash != "":
            return (
                jsonify({"error": MSG_UNAUTHORIZED, "detail": "invalid_credentials"}),
                HTTP_UNAUTHORIZED,
            )

        user_profile = {
            "id": user.get("id"),
            "nombre": user.get("nombre"),
            "mail": user.get("mail"),
            "score": user.get("score"),
            "rol": user.get("rol"),
            "carrera": user.get("carrera"),
        }

        token = generar_token(user.get("id"), user.get("rol"))

        return jsonify(
            {"token": token, "role": user.get("rol"), "user": user_profile}
        ), HTTP_OK

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        try:
            cursor.close()

        except Exception:
            pass

        try:
            conn.close()

        except Exception:
            pass


# pre:  mail es un string con formato de email válido.
# post: devuelve un diccionario con los datos del usuario si existe, None si no se encuentra.
def buscar_usuario_por_mail(mail):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, mail, contrasenia_hash, rol FROM usuario WHERE mail = %s",
        (mail,),
    )
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario


# pre:  el request incluye un JWT válido en el header Authorization.
# post: devuelve 200 confirmando el cierre de sesión. El cliente debe descartar el token.
@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    return jsonify({"mensaje": "Sesión cerrada con éxito"}), HTTP_OK
