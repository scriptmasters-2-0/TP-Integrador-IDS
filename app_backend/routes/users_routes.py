"""Rutas de la API para la gestión de usuarios.

Define los endpoints para crear, actualizar, consultar préstamos
y eliminar (baja lógica) usuarios del sistema.
"""

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
from validators import valid_id, valid_user, valid_user_update

users_bp = Blueprint("users", __name__)
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


@users_bp.route("/api/users/<int:user_id>/loans", methods=["GET"])
@requiere_auth(roles=["admin", "profesor", "bibliotecario", "alumno"])
def get_user_loans(user_id):
    """Obtiene los préstamos (reservas) de un usuario específico.

    Args:
        user_id (int): Identificador del usuario cuyos préstamos
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
            WHERE r.id_usuario = %(user_id)s
            ORDER BY r.fecha_retiro DESC
        """
        values = {"user_id": user_id}

        cursor.execute(sql_query, values)
        loans = cursor.fetchall()

        if len(loans) == 0:
            return (
                jsonify({"message": MSG_NOT_FOUND}),
                HTTP_NOT_FOUND,
            )

        return jsonify(loans), HTTP_OK

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


@users_bp.route("/api/users", methods=["POST"])
@requiere_auth(roles=["admin"])
def create_user():
    """Crea un nuevo usuario en el sistema.

    Espera un cuerpo JSON con los datos del usuario: nombre, mail,
    score (opcional, por defecto 0), rol y carrera.

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

    is_valid, error = valid_user(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    cursor = None

    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuario (nombre, mail, score, rol, carrera)
            VALUES (%(nombre)s, %(mail)s, %(score)s, %(rol)s, %(carrera)s)
        """
        values = {
            "nombre": data.get("nombre"),
            "mail": data.get("mail"),
            "score": data.get("score") if data.get("score") is not None else 0,
            "rol": data.get("rol"),
            "carrera": data.get("carrera"),
        }
        cursor.execute(sql, values)
        conn.commit()
        user_id = cursor.lastrowid

        user = {
            "id": user_id,
            "nombre": data.get("nombre"),
            "mail": data.get("mail"),
            "score": data.get("score") if data.get("score") is not None else 0,
            "rol": data.get("rol"),
            "carrera": data.get("carrera"),
        }

        return jsonify(user), HTTP_CREATED

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


@users_bp.route("/api/users/<int:user_id>", methods=["PUT"])
@requiere_auth(roles=["admin"])
def update_user(user_id):
    """Actualiza los datos de un usuario existente.

    Permite modificar cualquier campo del usuario mediante un cuerpo
    JSON con los campos a actualizar.

    Args:
        user_id (int): Identificador del usuario a actualizar.

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

    if valid_id(user_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()

    except Exception:
        data = None

    is_valid, error = valid_user_update(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    keysToUpdate = data.keys()

    set_clause = ", ".join([f"{f} = %({f})s" for f in keysToUpdate])
    data.update({"user_id": user_id})

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = f"UPDATE usuario SET {set_clause} WHERE id = %(user_id)s"
        cursor.execute(sql, data)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        cursor.execute(
            """
            SELECT id, nombre, mail, score, rol, carrera
            FROM usuario
            WHERE id = %(user_id)s
            """,
            {"user_id": user_id},
        )

        user = cursor.fetchone()

        return jsonify(user), HTTP_OK

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


@users_bp.route("/api/usuarios/<int:id_usuario>", methods=["DELETE"])
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
