"""Rutas de la API para la gestión de usuarios.

Define los endpoints para crear, actualizar, consultar préstamos
y eliminar usuarios del sistema.
"""

import logging
from datetime import timezone
from zoneinfo import ZoneInfo

import mysql.connector
from flask import Blueprint, jsonify, request

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_CONFLICT,
    HTTP_CREATED,
    HTTP_FORBIDDEN,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MSG_BAD_REQUEST,
    MSG_CONFLICT,
    MSG_DB_CONNECTION_FAILED,
    MSG_FORBIDDEN,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
)
from paginacion import construir_respuesta_paginada, obtener_parametros_paginacion
from routes.auth_route import hashear_contrasenia, requiere_auth
from validators import valid_contrasenia, valid_id, valid_usuario, valid_usuario_update

usuarios_bp = Blueprint("usuarios", __name__)
logger = logging.getLogger(__name__)
ARGENTINA_TZ = ZoneInfo("America/Argentina/Buenos_Aires")
DUPLICATE_ENTRY_ERRNO = 1062
FOREIGN_KEY_CONSTRAINT_ERRNO = 1451


def _datetime_to_argentina_iso(value):
    """Convierte un datetime de base de datos a ISO 8601 en hora argentina."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(ARGENTINA_TZ).isoformat(timespec="seconds")


def format_usuario_reserva(row):
    """Formatea una reserva de usuario para evitar serialización GMT de Flask."""
    nombre_articulo = row.get("nombre_articulo")
    return {
        "id": row.get("id"),
        "id_reservado": row.get("id_reservado"),
        "nombre_articulo": nombre_articulo,
        "nombre_art": nombre_articulo,
        "estado_reserva": row.get("estado_reserva"),
        "fecha_retiro": _datetime_to_argentina_iso(row.get("fecha_retiro")),
        "fecha_regreso": _datetime_to_argentina_iso(row.get("fecha_regreso")),
    }


@usuarios_bp.route("/api/usuarios", methods=["GET"])
@requiere_auth(roles=["admin", "bibliotecario"])
def obtener_todos_los_usuarios():
    """Lista todos los usuarios registrados.

    Returns:
        tuple: JSON con la lista de usuarios y código HTTP 200,
            o un error con su código correspondiente.

    """
    nombre_usuario = request.args.get("usuario")
    pagination, error = obtener_parametros_paginacion(request.args)
    if error:
        return jsonify({"error": error}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        consulta_total = "SELECT COUNT(*) AS total FROM usuario"
        consulta_usuarios = """
            SELECT id, nombre, email, rol, carrera, activo
            FROM usuario
        """
        params = dict(pagination)
        if nombre_usuario:
            consulta_total += " WHERE nombre LIKE %(nombre_usuario)s"
            consulta_usuarios += " WHERE nombre LIKE %(nombre_usuario)s"
            params["nombre_usuario"] = f"%{nombre_usuario}%"

        consulta_usuarios += " ORDER BY nombre LIMIT %(limit)s OFFSET %(offset)s"

        cursor.execute(consulta_total, params)
        total = cursor.fetchone()["total"]

        cursor.execute(consulta_usuarios, params)
        usuarios = cursor.fetchall()

        return (
            jsonify(
                construir_respuesta_paginada(
                    usuarios,
                    total,
                    request,
                    pagination["limit"],
                    pagination["offset"],
                )
            ),
            HTTP_OK,
        )

    except mysql.connector.Error as query_err:
        logger.error("Error en la consulta a la base de datos en get_all_usuarios: %s", query_err)

        return jsonify(
            {"error": "Error interno del servidor: fallo en la consulta a la base de datos"}
        ), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        logger.exception("Error inesperado en get_all_usuarios")
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR
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
@requiere_auth(roles=["admin", "bibliotecario"])
def obtener_id_usuario(usuario_id):
    """Obtiene un usuario por su identificador.

    Args:
        usuario_id (int): Identificador único del usuario a consultar.

    Returns:
        tuple: JSON con el usuario y código HTTP 200,
            o un error con su código correspondiente.

    """
    if valid_id(usuario_id) is None:
        return jsonify({"error": "Formato de ID de usuario inválido"}), HTTP_BAD_REQUEST

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
                {"error": f"Usuario con ID {usuario_id} no encontrado"}
            ), HTTP_NOT_FOUND

        return jsonify(usuario), HTTP_OK

    except mysql.connector.Error as query_err:
        logger.error("Error de consulta a la base de datos en get_usuario_by_id: %s", query_err)

        return jsonify(
            {"error": "Error interno del servidor: fallo en la consulta a la base de datos"}
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


def eliminar_usuario_db(id_usuario):
    """Elimina un usuario de la base de datos.

    Args:
        id_usuario (int): Identificador del usuario a eliminar.
            Debe ser un entero positivo.

    Returns:
        tuple: (eliminado, error, status), con error y status en None
            cuando la eliminación fue procesada sin fallos.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return False, MSG_DB_CONNECTION_FAILED, HTTP_INTERNAL_SERVER_ERROR

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM usuario WHERE id = %s", (id_usuario,))
        conexion.commit()
        return cursor.rowcount > 0, None, None
    except mysql.connector.Error as err:
        if err.errno == FOREIGN_KEY_CONSTRAINT_ERRNO:
            return (
                False,
                "No se pudo eliminar el usuario por una restricción de base de datos",
                HTTP_CONFLICT,
            )
        return False, MSG_INTERNAL_SERVER_ERROR, HTTP_INTERNAL_SERVER_ERROR
    except Exception:
        return False, MSG_INTERNAL_SERVER_ERROR, HTTP_INTERNAL_SERVER_ERROR
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if conexion:
                conexion.close()
        except Exception:
            pass


@usuarios_bp.route("/api/usuarios/<int:usuario_id>/reservas", methods=["GET"])
@requiere_auth(roles=["admin", "profesor", "bibliotecario", "alumno"])
def obtener_reservas_usuario(usuario_id):
    """Obtiene los préstamos (reservas) de un usuario específico.

    Args:
        usuario_id (int): Identificador del usuario cuyos préstamos
            se desean consultar.

    Returns:
        tuple: Respuesta JSON con la lista de préstamos del usuario
            y código HTTP 200, o un mensaje de error con el código
            correspondiente (404 si el usuario no existe, 500 si hay
            error interno).

    """
    pagination, error = obtener_parametros_paginacion(request.args)
        
    if error:
        return jsonify({"error": error}), HTTP_BAD_REQUEST
        
    if (
        request.usuario_rol not in ("admin", "bibliotecario")
        and usuario_id != request.usuario_id
    ):
        return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM usuario WHERE id = %(usuario_id)s",
            {"usuario_id": usuario_id},
        )
        if not cursor.fetchone():
            return (
                jsonify({"error": MSG_NOT_FOUND}),
                HTTP_NOT_FOUND,
            )

        cursor.execute(
            "SELECT COUNT(*) AS total FROM reserva WHERE id_usuario = %(usuario_id)s",
            {"usuario_id": usuario_id},
        )

        total = cursor.fetchone()["total"]

        consulta_sql = """
        SELECT reservacion.id,
            reservacion.id_reservado,
            a.nombre_art AS nombre_articulo,
            reservacion.estado_reserva,
            reservacion.fecha_retiro,
            reservacion.fecha_regreso
            FROM reserva reservacion
            LEFT JOIN articulos a ON reservacion.id_reservado = a.id
            WHERE reservacion.id_usuario = %(usuario_id)s
            ORDER BY reservacion.fecha_retiro LIMIT %(limit)s OFFSET %(offset)s
        """
        values = {**pagination, "usuario_id": usuario_id}

        cursor.execute(consulta_sql, values)
        reservas = [format_usuario_reserva(fila) for fila in cursor.fetchall()]

        return (
        jsonify(
            construir_respuesta_paginada(
                reservas,
                total,
                request,
                pagination["limit"],
                pagination["offset"],
            )
        ),
            HTTP_OK,
        )

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
@requiere_auth(roles=["admin", "bibliotecario"])
def create_usuario():
    """Crea un nuevo usuario en el sistema.

    Espera un cuerpo JSON con los datos del usuario: nombre, email,
    rol y carrera.

    Returns:
        tuple: Respuesta JSON con los datos del usuario creado y código
            HTTP 201. Retorna 400 si los datos son inválidos, 409 si
            hay conflicto (duplicado), o 500 si hay error interno.

    Raises:
        mysql.connector.Error: Si ocurre un error de base de datos,
            incluyendo entradas duplicadas (errno 1062).

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
    rol = data.get("rol") or "alumno"

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuario (nombre, email, rol, carrera, contrasenia_hash)
            VALUES (%(nombre)s, %(email)s, %(rol)s, %(carrera)s, %(contrasenia_hash)s)
        """
        values = {
            "nombre": data.get("nombre"),
            "email": data.get("email"),
            "rol": rol,
            "carrera": data.get("carrera"),
            "contrasenia_hash": contrasenia_hash,
        }
        cursor.execute(sql, values)
        conn.commit()
        usuario_id = cursor.lastrowid

        usuario = {
            "id": usuario_id,
            "nombre": data.get("nombre"),
            "email": data.get("email"),
            "rol": rol,
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
@requiere_auth(roles=["admin", "bibliotecario"])
def obtener_usuario(usuario_id):
    """Descripción: función get_usuario."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, email, rol, carrera, activo FROM usuario WHERE id = %s",
            (usuario_id,),
        )
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND
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
@requiere_auth(roles=["admin", "bibliotecario", "alumno", "profesor"])
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
    if valid_id(usuario_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()

    except Exception:
        data = None

    if request.usuario_rol in ("alumno", "profesor"):
        if usuario_id != request.usuario_id:
            return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN

        if not isinstance(data, dict) or set(data.keys()) != {"contrasenia"}:
            return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN

        contrasenia = data.get("contrasenia")
        is_valid, error = valid_contrasenia(contrasenia)
        if not is_valid:
            return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

        set_clause = "contrasenia_hash = %(contrasenia_hash)s"
        data = {
            "contrasenia_hash": hashear_contrasenia(contrasenia),
            "usuario_id": usuario_id,
        }

    else:
        is_valid, error = valid_usuario_update(data)
        if not is_valid:
            return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

        if "activo" in data:
            data["activo"] = 1 if data.get("activo") in (True, 1, "1") else 0

        keysToUpdate = data.keys()

        set_clause = ", ".join([f"{f} = %({f})s" for f in keysToUpdate])
        data.update({"usuario_id": usuario_id})

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = f"UPDATE usuario SET {set_clause} WHERE id = %(usuario_id)s"
        cursor.execute(sql, data)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        cursor.execute(
            """
            SELECT id, nombre, email, rol, carrera, activo
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
@requiere_auth(roles=["admin", "bibliotecario"])
def eliminar_usuario(id_usuario):
    """Elimina un usuario por su id.

    El request debe incluir un JWT válido con rol admin en el header Authorization.

    Args:
        id_usuario (int): Entero positivo con el id del usuario a eliminar.

    Returns:
        tuple: JSON con mensaje de éxito y código 200,
               404 si el usuario no existe, 400 si el ID es inválido.

    """
    if id_usuario <= 0:
        return jsonify({"error": "ID inválido"}), HTTP_BAD_REQUEST

    eliminado, error, status = eliminar_usuario_db(id_usuario)
    if error:
        return jsonify({"error": error}), status
    if eliminado:
        return jsonify({"mensaje": "Usuario eliminado con éxito"}), HTTP_OK
    return jsonify({"error": "Usuario no encontrado"}), HTTP_NOT_FOUND
