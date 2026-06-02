"""Rutas para los endpoints de autenticación.

Incluye funciones de utilidad para hasheo de contraseñas, generación y
decodificación de tokens JWT, y un decorador para proteger rutas que
requieren autenticación.
"""

from functools import wraps

import bcrypt
import jwt
from flask import Blueprint, jsonify, request

from config import JWT_ALGORITHM, JWT_SECRET
from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    MSG_BAD_REQUEST,
    MSG_DB_CONNECTION_FAILED,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
    MSG_UNAUTHORIZED,
)
from validators import valid_login

auth_bp = Blueprint("auth", __name__)


def hashear_password(password):
    """Genera el hash de una contraseña usando bcrypt.

    Args:
        password (str): Contraseña en texto plano a hashear.

    Returns:
        str: Hash de la contraseña codificado en UTF-8.

    """
    hash_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    return hash_bytes.decode("utf-8")


def validar_password(password, password_hash):
    """Verifica si una contraseña coincide con su hash.

    Args:
        password (str): Contraseña en texto plano a verificar.
        password_hash (str): Hash almacenado contra el cual comparar.

    Returns:
        bool: True si la contraseña coincide con el hash, False en caso contrario.

    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    except (ValueError, TypeError):
        print("Error al verificar la contraseña")
        return False


def generar_token(user_id, rol):
    """Genera un token JWT con el ID de usuario y su rol.

    Args:
        user_id (int): Identificador único del usuario.
        rol (str): Rol del usuario en el sistema.

    Returns:
        str: Token JWT codificado.

    """
    payload = {
        "user_id": user_id,
        "rol": rol,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token(token):
    """Decodifica y valida un token JWT.

    Args:
        token (str): Token JWT a decodificar.

    Returns:
        tuple: Una tupla (payload, mensaje) donde payload es un diccionario
            con los datos del token si es válido o None si no lo es, y
            mensaje es un string indicando el estado ("Valid", "Expired"
            o "Invalid").

    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]), "Valid"

    except jwt.ExpiredSignatureError:
        return None, "Expired"

    except jwt.InvalidTokenError:
        return None, "Invalid"


def extraer_token_del_header():
    """Extrae el token JWT del header Authorization de la petición.

    Espera un header con formato "Bearer <token>".

    Returns:
        tuple: Una tupla (token, mensaje) donde token es el string del JWT
            si se extrajo correctamente o None si el formato es incorrecto,
            y mensaje indica el estado ("Ok" o "Incorrect token type").

    """
    header = request.headers.get("Authorization", "")

    if not header.startswith("Bearer "):
        return None, "Incorrect token type"

    return header[len("Bearer ") :].strip(), "Ok"


# decorator
def requiere_auth(roles):
    """Decorador que protege una ruta requiriendo autenticación y un rol específico.

    Verifica que la petición incluya un token JWT válido en el header
    Authorization y que el rol del usuario coincida con el rol requerido.

    Args:
        roles (str): Roles requeridos para acceder a la ruta protegida.

    Returns:
        function: Decorador que envuelve la función de ruta con la
            validación de autenticación y autorización.

    """

    def wrapperGenerator(route):

        @wraps(route)
        def wrapper(*args, **kwargs):
            token, tokenError = extraer_token_del_header()

            if token is None:
                return jsonify({"error": tokenError}), HTTP_UNAUTHORIZED

            payload, payloadError = decodificar_token(token)

            if payload is None:
                return jsonify({"error": payloadError}), HTTP_UNAUTHORIZED

            if payload.get("rol") not in roles:
                return jsonify({"error": MSG_UNAUTHORIZED}), HTTP_UNAUTHORIZED

            request.user_id = payload.get("user_id")
            request.user_rol = payload.get("rol")

            return route(*args, **kwargs)

        return wrapper

    return wrapperGenerator


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Autentica a un usuario mediante nombre de usuario y contraseña.

    Recibe las credenciales en el cuerpo de la petición como JSON,
    las valida contra la base de datos y, si son correctas, retorna
    un token JWT junto con el perfil del usuario.

    Returns:
        tuple: JSON con el token, rol y perfil del usuario si la
            autenticación es exitosa, o un mensaje de error con el
            código HTTP correspondiente.

    """
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

        sql_query = """
            SELECT id, nombre, mail, score, rol, carrera, password_hash
            FROM usuario
            WHERE nombre = %(value)s
            LIMIT 1
        """
        value = {"value": username}

        cursor.execute(sql_query, value)

        user = cursor.fetchone()
        if not user:
            return (
                jsonify({"error": MSG_UNAUTHORIZED, "detail": "invalid_credentials"}),
                HTTP_UNAUTHORIZED,
            )

        password_hash = user.get("password_hash", "")

        if not validar_password(password, password_hash) and password_hash != "":
            print(
                validar_password(
                    "password",
                    "$2b$12$KIXe8T3G/R/y1P.4yHxz/e/N.t.C79.A8aZ3vA.j1gX.oDkM3p6X2",
                )
            )
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


@auth_bp.route("/api/auth/logout", methods=["POST"])
@requiere_auth(roles=["admin"])
def logout():
    """Cierra la sesión del usuario autenticado.

    El request debe incluir un JWT válido en el header Authorization.
    El cliente debe descartar el token al recibir la respuesta.

    Returns:
        tuple: JSON con mensaje de confirmación y código 200.

    """
    return jsonify({"mensaje": "Sesión cerrada con éxito"}), HTTP_OK


@auth_bp.route("/api/auth/me", methods=["GET"])
@requiere_auth(roles=["admin", "alumno", "profesor", "bibliotecario"])
def obtener_perfil():
    """Obtiene el perfil del usuario autenticado.

    El request debe incluir un JWT válido en el header Authorization.
    Retorna los datos del usuario extraídos del token.

    Returns:
        tuple: JSON con los datos del usuario (id, rol) y código 200,
            o mensaje de error con código 401 si el token es inválido.

    """
    conn = obtener_conexion()

    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        sql_query = """
            SELECT id, nombre, mail, score, rol, carrera, password_hash
            FROM usuario
            WHERE id = %(user_id)s
            LIMIT 1
        """
        value = {"user_id": request.user_id}

        cursor.execute(sql_query, value)

        user = cursor.fetchone()
        if not user:
            return (
                jsonify({"error": MSG_NOT_FOUND}),
                HTTP_NOT_FOUND,
            )

        user_profile = {
            "id": user.get("id"),
            "nombre": user.get("nombre"),
            "mail": user.get("mail"),
            "score": user.get("score"),
            "rol": user.get("rol"),
            "carrera": user.get("carrera"),
        }

        return jsonify({"user": user_profile}), HTTP_OK

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
