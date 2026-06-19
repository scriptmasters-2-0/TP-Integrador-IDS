"""Rutas para los endpoints de autenticación.

Incluye funciones de utilidad para hasheo de contraseñas, generación y
decodificación de tokens JWT, y un decorador para proteger rutas que
requieren autenticación.
"""

from functools import wraps
import logging

import bcrypt
import jwt
import mysql.connector
from flask import Blueprint, jsonify, request
from mysql.connector import errorcode

from config import JWT_ALGORITMO, JWT_SECRETO
from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_CONFLICT,
    HTTP_CREATED,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    MSG_BAD_REQUEST,
    MSG_CONFLICT,
    MSG_DB_CONNECTION_FAILED,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
    MSG_UNAUTHORIZED,
)
from validators import valid_login, valid_usuario

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


def hashear_contrasenia(contrasenia):
    """Genera el hash de una contraseña usando bcrypt.

    Args:
        contrasenia (str): Contraseña en texto plano a hashear.

    Returns:
        str: Hash de la contraseña codificado en UTF-8.

    """
    hash_bytes = bcrypt.hashpw(contrasenia.encode("utf-8"), bcrypt.gensalt())

    return hash_bytes.decode("utf-8")


def validar_contrasenia(contrasenia, contrasenia_hash):
    """Verifica si una contraseña coincide con su hash.

    Args:
        contrasenia (str): Contraseña en texto plano a verificar.
        contrasenia_hash (str): Hash almacenado contra el cual comparar.

    Returns:
        bool: True si la contraseña coincide con el hash, False en caso contrario.

    """
    try:
        return bcrypt.checkpw(contrasenia.encode("utf-8"), contrasenia_hash.encode("utf-8"))

    except (ValueError, TypeError):
        logger.warning("Error al verificar la contraseña")
        return False


def generar_token(usuario_id, rol):
    """Genera un token JWT con el ID de usuario y su rol.

    Args:
        usuario_id (int): Identificador único del usuario.
        rol (str): Rol del usuario en el sistema.

    Returns:
        str: Token JWT codificado.

    """
    payload = {
        "usuario_id": usuario_id,
        "rol": rol,
    }

    return jwt.encode(payload, JWT_SECRETO, algorithm=JWT_ALGORITMO)


def decodificar_token(token):
    """Decodifica y valida un token JWT.

    Args:
        token (str): Token JWT a decodificar.

    Returns:
        tuple: Una tupla (payload, mensaje) donde payload es un diccionario
            con los datos del token si es válido o None si no lo es, y
            mensaje es un string indicando el estado ("Válido", "Token expirado"
            o "Token inválido").

    """
    try:
        return jwt.decode(token, JWT_SECRETO, algorithms=[JWT_ALGORITMO]), "Válido"

    except jwt.ExpiredSignatureError:
        return None, "Token expirado"

    except jwt.InvalidTokenError:
        return None, "Token inválido"


def extraer_token_del_header():
    """Extrae el token JWT del header Authorization de la petición.

    Espera un header con formato "Bearer <token>".

    Returns:
        tuple: Una tupla (token, mensaje) donde token es el string del JWT
            si se extrajo correctamente o None si el formato es incorrecto,
            y mensaje indica el estado ("OK" o "Tipo de token incorrecto").

    """
    header = request.headers.get("Authorization", "")

    if not header.startswith("Bearer "):
        return None, "Tipo de token incorrecto"

    return header[len("Bearer ") :].strip(), "OK"


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
            """Descripción: función wrapper."""
            token, tokenError = extraer_token_del_header()

            if token is None:
                return jsonify({"error": tokenError}), HTTP_UNAUTHORIZED

            payload, payloadError = decodificar_token(token)

            if payload is None:
                return jsonify({"error": payloadError}), HTTP_UNAUTHORIZED

            if payload.get("rol") not in roles:
                return jsonify({"error": MSG_UNAUTHORIZED}), HTTP_UNAUTHORIZED

            request.usuario_id = payload.get("usuario_id")
            request.usuario_rol = payload.get("rol")

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

    email = data.get("email")
    contrasenia = data.get("contrasenia")

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        sql_query = """
            SELECT id, nombre, email, puntaje, rol, carrera, contrasenia_hash, activo
            FROM usuario
            WHERE email = %(value)s
            LIMIT 1
        """
        value = {"value": email}

        cursor.execute(sql_query, value)

        usuario = cursor.fetchone()
        if not usuario:
            return (
                jsonify({"error": MSG_UNAUTHORIZED, "detail": "invalid_credentials"}),
                HTTP_UNAUTHORIZED,
            )

        contrasenia_hash = usuario.get("contrasenia_hash", "")

        if not validar_contrasenia(contrasenia, contrasenia_hash) and contrasenia_hash != "":
            return (
                jsonify({"error": MSG_UNAUTHORIZED, "detail": "invalid_credentials"}),
                HTTP_UNAUTHORIZED,
            )

        usuario_profile = {
            "id": usuario.get("id"),
            "nombre": usuario.get("nombre"),
            "email": usuario.get("email"),
            "puntaje": usuario.get("puntaje"),
            "rol": usuario.get("rol"),
            "carrera": usuario.get("carrera"),
            "activo": bool(usuario.get("activo", True)),
        }

        token = generar_token(usuario.get("id"), usuario.get("rol"))

        return jsonify({"token": token, "rol": usuario.get("rol"), "usuario": usuario_profile}), HTTP_OK

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
            SELECT
                u.id,
                u.nombre,
                u.email,
                u.puntaje,
                u.rol,
                u.carrera,
                u.contrasenia_hash,
                COUNT(p.id) AS penalizaciones
            FROM usuario u
            LEFT JOIN penalizacion p ON u.id = p.id_usuario
            WHERE u.id = %(usuario_id)s AND u.activo = 1
            GROUP BY u.id
            LIMIT 1;
        """
        value = {"usuario_id": request.usuario_id}

        cursor.execute(sql_query, value)

        usuario = cursor.fetchone()
        if not usuario:
            return (
                jsonify({"error": MSG_NOT_FOUND}),
                HTTP_NOT_FOUND,
            )

        usuario_profile = {
            "id": usuario.get("id"),
            "nombre": usuario.get("nombre"),
            "email": usuario.get("email"),
            "puntaje": usuario.get("puntaje"),
            "rol": usuario.get("rol"),
            "carrera": usuario.get("carrera"),
            "penalizaciones": usuario.get("penalizaciones", 0),
        }

        return jsonify({"usuario": usuario_profile}), HTTP_OK

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


@auth_bp.route("/api/auth/logup", methods=["POST"])
def logup():
    """Registra un nuevo usuario y devuelve token JWT.

    Crea un usuario con rol 'alumno' y guarda el hash de la contraseña.
    Retorna token y perfil del usuario al crearse exitosamente.
    """
    try:
        data = request.get_json()
    except Exception:
        data = None

    if not data:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    is_valid, error = valid_usuario(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    contrasenia = data.get("contrasenia")
    if contrasenia is None or not isinstance(contrasenia, str) or contrasenia.strip() == "":
        return jsonify({"error": MSG_BAD_REQUEST, "detail": "missing:contrasenia"}), HTTP_BAD_REQUEST

    contrasenia_hash = hashear_contrasenia(contrasenia)

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuario (nombre, email, puntaje, rol, carrera, contrasenia_hash)
            VALUES (%(nombre)s, %(email)s, %(puntaje)s, %(rol)s, %(carrera)s, %(contrasenia_hash)s)
        """
        values = {
            "nombre": data.get("nombre"),
            "email": data.get("email"),
            "puntaje": 0,
            "rol": "alumno",
            "carrera": data.get("carrera"),
            "contrasenia_hash": contrasenia_hash,
        }
        cursor.execute(sql, values)
        conn.commit()
        usuario_id = cursor.lastrowid

        usuario_profile = {
            "id": usuario_id,
            "nombre": data.get("nombre"),
            "email": data.get("email"),
            "puntaje": 0,
            "rol": "alumno",
            "carrera": data.get("carrera"),
        }

        token = generar_token(usuario_id, "alumno")

        return jsonify({"token": token, "rol": "alumno", "usuario": usuario_profile}), HTTP_CREATED

    except mysql.connector.Error as err:
        try:
            if err.errno == errorcode.ER_DUP_ENTRY:
                return (
                    jsonify({"error": MSG_CONFLICT, "detail": "duplicate_entry"}),
                    HTTP_CONFLICT,
                )
        except Exception:
            pass
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass
