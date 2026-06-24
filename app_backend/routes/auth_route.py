"""Rutas para los endpoints de autenticación.

Incluye funciones de utilidad para hasheo de contraseñas, generación y
decodificación de tokens JWT, y un decorador para proteger rutas que
requieren autenticación.
"""

import logging

import mysql.connector
from flask import Blueprint, jsonify, request
from mysql.connector import errorcode

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_CONFLICT,
    HTTP_CREATED,
    HTTP_FORBIDDEN,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    MSG_BAD_REQUEST,
    MSG_CONFLICT,
    MSG_DB_CONNECTION_FAILED,
    MSG_FORBIDDEN,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
    MSG_UNAUTHORIZED,
)
from utiles.autenticacion import generar_token, hashear_contrasenia, requiere_auth, validar_contrasenia
from validators import valid_contrasenia, valid_login, valid_usuario

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


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
            SELECT id, nombre, email, rol, carrera, contrasenia_hash, activo
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

        contrasenia_hash = usuario.get("contrasenia_hash") or ""

        if not contrasenia_hash or not validar_contrasenia(contrasenia, contrasenia_hash):
            return (
                jsonify({"error": MSG_UNAUTHORIZED, "detail": "invalid_credentials"}),
                HTTP_UNAUTHORIZED,
            )

        if usuario.get("activo") in (False, 0, "0"):
            return (
                jsonify({"error": MSG_FORBIDDEN, "detail": "inactive_user"}),
                HTTP_FORBIDDEN,
            )

        usuario_profile = {
            "id": usuario.get("id"),
            "nombre": usuario.get("nombre"),
            "email": usuario.get("email"),
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
@requiere_auth(roles=["admin", "alumno", "profesor", "bibliotecario"])
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
                u.padron,
                u.nombre,
                u.email,
                u.rol,
                u.carrera,
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
            "legajo": usuario.get("padron"),
            "nombre": usuario.get("nombre"),
            "email": usuario.get("email"),
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
    is_valid, error = valid_contrasenia(contrasenia)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    contrasenia_hash = hashear_contrasenia(contrasenia)

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuario (padron, nombre, email, rol, carrera, contrasenia_hash)
            VALUES (%(padron)s, %(nombre)s, %(email)s, %(rol)s, %(carrera)s, %(contrasenia_hash)s)
        """
        values = {
            "padron": data.get("padron"),
            "nombre": data.get("nombre"),
            "email": data.get("email"),
            "rol": "alumno",
            "carrera": data.get("carrera"),
            "contrasenia_hash": contrasenia_hash,
        }
        cursor.execute(sql, values)
        conn.commit()
        usuario_id = cursor.lastrowid

        usuario_profile = {
            "id": usuario_id,
            "padron": data.get("padron"),
            "nombre": data.get("nombre"),
            "email": data.get("email"),
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
