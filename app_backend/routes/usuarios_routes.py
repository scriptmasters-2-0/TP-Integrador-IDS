"""Rutas de la API para la gestión de usuarios.

Define los endpoints para crear, actualizar, consultar préstamos
y eliminar (baja lógica) usuarios del sistema.
"""

import logging

import mysql.connector
from flask import Blueprint, jsonify, request

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_CONFLICT,
    HTTP_CREATED,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MSG_BAD_REQUEST,
    MSG_CONFLICT,
    MSG_DB_CONNECTION_FAILED,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
)
from routes.auth_route import requiere_auth
from validators import valid_id, valid_usuario, valid_usuario_update

logging.basicConfig(level=logging.ERROR)

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/api/usuario", methods=["GET"])
def get_all_usuarios():
    """Lista todos los usuarios registrados.

    Returns:
        tuple: JSON con la lista de usuarios y código HTTP 200,
            o un error con su código correspondiente.

    """
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, nombre, email, rol FROM usuario"
        cursor.execute(query)
        usuarios = cursor.fetchall()

        return jsonify(usuarios), HTTP_OK

    except mysql.connector.Error as query_err:
        logging.error(f"Database query error in get_all_usuarios: {query_err}")

        return jsonify(
            {"error": "Internal server error: Database query failed"}
        ), HTTP_INTERNAL_SERVER_ERROR

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


@usuarios_bp.route("/api/usuario/<int:usuario_id>", methods=["GET"])
def get_usuario_by_id(usuario_id):
    """Obtiene un usuario por su identificador.

    Args:
        usuario_id (int): Identificador único del usuario a consultar.

    Returns:
        tuple: JSON con el usuario y código HTTP 200,
            o un error con su código correspondiente.

    """
    if valid_id(usuario_id) is None:
        return jsonify({"error": "Invalid usuario ID format"}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, nombre, email, rol FROM usuario WHERE id = %s"
        cursor.execute(query, (usuario_id,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify(
                {"error": f"User with ID {usuario_id} not found"}
            ), HTTP_NOT_FOUND

        return jsonify(usuario), HTTP_OK

    except mysql.connector.Error as query_err:
        logging.error(f"Database query error in get_usuario_by_id: {query_err}")

        return jsonify(
            {"error": "Internal server error: Database query failed"}
        ), HTTP_INTERNAL_SERVER_ERROR

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


DUPLICATE_ENTRY_ERRNO = 1062


def desactivar_usuario_db(id_usuario):
    """Marca un usuario como inactivo en la base de datos (baja lógica).

    Args:
        id_usuario (int): Identificador del usuario a desactivar.
            Debe ser un entero positivo.

    Returns:
        bool: True si el usuario fue actualizado exitosamente,
            False si no existía.

    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("UPDATE usuario SET activo = FALSE WHERE id = %s", (id_usuario,))
    conexion.commit()
    actualizado = cursor.rowcount > 0
    cursor.close()
    conexion.close()
    return actualizado


@usuarios_bp.route("/api/usuarios/<int:usuario_id>/reservas", methods=["GET"])
@requiere_auth(roles=["admin", "profesor", "bibliotecario", "alumno"])
def get_usuario_reservas(usuario_id):
    """Obtiene los préstamos (reservas) de un usuario específico.

    Args:
        usuario_id (int): Identificador del usuario cuyos préstamos
            se desean consultar.

    Returns:
        tuple: Respuesta JSON con la lista de préstamos del usuario
            y código HTTP 200, o un mensaje de error con el código
            correspondiente (404 si no tiene préstamos, 500 si hay
            error interno).

    """
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        sql_query = """
            SELECT r.id,
                   r.id_reservado,
                   a.nombre_art AS nombre_articulo,
                   r.estado_reserva,
                   r.fecha_retiro,
                   r.fecha_regreso
            FROM reserva r
            LEFT JOIN articulos a ON r.id_reservado = a.id
            WHERE r.id_usuario = %(usuario_id)s
            ORDER BY r.fecha_retiro DESC
        """
        values = {"usuario_id": usuario_id}

        cursor.execute(sql_query, values)
        reservas = cursor.fetchall()

        if len(reservas) == 0:
            return (
                jsonify({"message": MSG_NOT_FOUND}),
                HTTP_NOT_FOUND,
            )

        return jsonify(reservas), HTTP_OK

    except Exception:
        return (
            jsonify({"error": MSG_INTERNAL_SERVER_ERROR}),
            HTTP_INTERNAL_SERVER_ERROR,
        )

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


@usuarios_bp.route("/api/usuarios", methods=["POST"])
@requiere_auth(roles=["admin"])
def create_usuario():
    """Crea un nuevo usuario en el sistema.

    Espera un cuerpo JSON con los datos del usuario: nombre, email,
    puntaje (opcional, por defecto 0), rol y carrera.

    Returns:
        tuple: Respuesta JSON con los datos del usuario creado y código
            HTTP 201. Retorna 400 si los datos son inválidos, 409 si
            hay conflicto (duplicado), o 500 si hay error interno.

    Raises:
        mysql.connector.Error: Si ocurre un error de base de datos,
            incluyendo entradas duplicadas (errno 1062).

    """
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    try:
        data = request.get_json()
    except Exception:
        data = None

    if not data:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    is_valid, error = valid_usuario(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    cursor = None

    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuario (nombre, email, puntaje, rol, carrera)
            VALUES (%(nombre)s, %(email)s, %(puntaje)s, %(rol)s, %(carrera)s)
        """
        values = {
            "nombre": data.get("nombre"),
            "email": data.get("email"),
            "puntaje": data.get("puntaje") if data.get("puntaje") is not None else 0,
            "rol": data.get("rol"),
            "carrera": data.get("carrera"),
        }
        cursor.execute(sql, values)
        conn.commit()
        usuario_id = cursor.lastrowid

        usuario = {
            "id": usuario_id,
            "nombre": data.get("nombre"),
            "email": data.get("email"),
            "puntaje": data.get("puntaje") if data.get("puntaje") is not None else 0,
            "rol": data.get("rol"),
            "carrera": data.get("carrera"),
        }

        return jsonify(usuario), HTTP_CREATED

    except mysql.connector.Error as err:
        try:
            if err.errno == DUPLICATE_ENTRY_ERRNO:
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


@usuarios_bp.route("/api/usuarios/<int:usuario_id>", methods=["GET"])
@requiere_auth(roles=["admin"])
def get_usuario(usuario_id):
    """Descripción: función get_usuario."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, email, puntaje, rol, carrera FROM usuario WHERE id = %s",
            (usuario_id,),
        )
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND
        return jsonify(usuario), HTTP_OK
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


@usuarios_bp.route("/api/usuarios/<int:usuario_id>", methods=["PUT"])
@requiere_auth(roles=["admin"])
def update_usuario(usuario_id):
    """Actualiza los datos de un usuario existente.

    Permite modificar cualquier campo del usuario mediante un cuerpo
    JSON con los campos a actualizar.

    Args:
        usuario_id (int): Identificador del usuario a actualizar.

    Returns:
        tuple: Respuesta JSON con los datos actualizados del usuario
            y código HTTP 200. Retorna 400 si los datos son inválidos,
            404 si el usuario no existe, 409 si hay conflicto (duplicado),
            o 500 si hay error interno.

    Raises:
        mysql.connector.Error: Si ocurre un error de base de datos,
            incluyendo entradas duplicadas (errno 1062).

    """
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(usuario_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()

    except Exception:
        data = None

    is_valid, error = valid_usuario_update(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    keysToUpdate = data.keys()

    set_clause = ", ".join([f"{f} = %({f})s" for f in keysToUpdate])
    data.update({"usuario_id": usuario_id})

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = f"UPDATE usuario SET {set_clause} WHERE id = %(usuario_id)s"
        cursor.execute(sql, data)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        cursor.execute(
            """
            SELECT id, nombre, email, puntaje, rol, carrera
            FROM usuario
            WHERE id = %(usuario_id)s
            """,
            {"usuario_id": usuario_id},
        )

        usuario = cursor.fetchone()

        return jsonify(usuario), HTTP_OK

    except mysql.connector.Error as err:
        try:
            if err.errno == DUPLICATE_ENTRY_ERRNO:
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


@usuarios_bp.route("/api/usuarios/<int:id_usuario>", methods=["DELETE"])
@requiere_auth(roles=["admin"])
def eliminar_usuario(id_usuario):
    """Da de baja lógica a un usuario por su id.

    El request debe incluir un JWT válido con rol admin en el header Authorization.

    Args:
        id_usuario (int): Entero positivo con el id del usuario a dar de baja.

    Returns:
        tuple: JSON con mensaje de éxito y código 200,
               404 si el usuario no existe, 400 si el ID es inválido.

    """
    if id_usuario <= 0:
        return jsonify({"error": "ID inválido"}), HTTP_BAD_REQUEST

    if desactivar_usuario_db(id_usuario):
        return jsonify({"mensaje": "Usuario dado de baja con éxito"}), HTTP_OK
    return jsonify({"error": "Usuario no encontrado"}), HTTP_NOT_FOUND
