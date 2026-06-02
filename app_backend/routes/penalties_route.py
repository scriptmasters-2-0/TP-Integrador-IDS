"""Rutas de la API para la gestión de penalizaciones.

Define los endpoints para consultar, crear y actualizar penalizaciones
de usuarios en el sistema.
"""

import mysql.connector
from flask import Blueprint, jsonify, request

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MSG_BAD_REQUEST,
    MSG_DB_CONNECTION_FAILED,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
)
from routes.auth_route import requiere_auth
from validators import valid_id, valid_penalty_patch

penalties_bp = Blueprint("penalties", __name__)


def usuario_existe(id_usuario):
    """Verifica si un usuario existe en la base de datos.

    Args:
        id_usuario (int): Identificador del usuario a verificar.

    Returns:
        bool: True si el usuario existe en la BD, False en caso contrario.

    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM usuario WHERE id = %s", (id_usuario,))
    existe = cursor.fetchone() is not None
    cursor.close()
    conexion.close()
    return existe


def listar_penalizaciones_db():
    """Obtiene todas las penalizaciones de la base de datos.

    Returns:
        list[dict]: Lista de diccionarios con todas las penalizaciones de la BD.

    """
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM penalizacion")
    penalizaciones = cursor.fetchall()
    cursor.close()
    conexion.close()
    return penalizaciones


def crear_penalizacion_db(id_usuario, motivo):
    """Inserta una nueva penalización activa en la base de datos.

    Crea una penalización con duración de 15 días a partir de la
    fecha actual.

    Args:
        id_usuario (int): Identificador del usuario a penalizar.
            Debe ser un entero positivo.
        motivo (str): Motivo de la penalización. No debe estar vacío.

    Returns:
        int: Identificador generado para la nueva penalización.

    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO penalizacion (id_usuario, motivo, fecha_inicio, fecha_fin, activa)
        VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 15 DAY), TRUE)
        """,
        (id_usuario, motivo),
    )
    conexion.commit()
    id_generado = cursor.lastrowid
    cursor.close()
    conexion.close()
    return id_generado


def format_penalty(row):
    """Formatea una fila de penalización de la BD como respuesta de la API.

    Args:
        row (dict): Diccionario con los datos de la penalización obtenidos
            de la base de datos.

    Returns:
        dict: Diccionario con los campos formateados para la respuesta
            de la API.

    """
    return {
        "id": row.get("id"),
        "userId": row.get("id_usuario"),
        "loanId": row.get("id_reserva"),
        "reason": row.get("motivo"),
        "status": "Activa" if row.get("activa") else "Levantada",
        "severity": row.get("severity"),
        "notes": row.get("motivo"),
        "createdAt": (
            row.get("fecha_inicio").isoformat() if row.get("fecha_inicio") else None
        ),
        "resolvedAt": (
            row.get("fecha_fin").isoformat() if row.get("fecha_fin") else None
        ),
    }


def obtener_penalizacion_por_id(id_penalizacion):
    """Obtiene una penalización por su identificador.

    Args:
        id_penalizacion (int): Identificador de la penalización a buscar.

    Returns:
        dict | None: Diccionario con los datos de la penalización si existe,
            None si no se encuentra.

    """
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM penalizacion WHERE id = %s", (id_penalizacion,))
    penalizacion = cursor.fetchone()
    cursor.close()
    conexion.close()
    return penalizacion


@penalties_bp.route("/api/penalties/<int:penalty_id>", methods=["GET"])
def get_penalty(penalty_id):
    """Obtiene una penalización por su identificador.

    Args:
        penalty_id (int): Identificador de la penalización.

    Returns:
        tuple: Respuesta JSON con la penalización y código HTTP 200,
            o un mensaje de error con el código correspondiente.

    Raises:
        mysql.connector.Error: Si ocurre un error de conexión a la BD.

    """
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(penalty_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id,
                   id_usuario,
                   id_reserva,
                   motivo,
                   fecha_inicio,
                   fecha_fin,
                   activa,
                   severity
            FROM penalizacion
            WHERE id = %(penalty_id)s
            """,
            {"penalty_id": penalty_id},
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify(format_penalty(row)), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

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


@penalties_bp.route("/api/penalties/<int:penalty_id>", methods=["PATCH"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def patch_penalty(penalty_id):  # noqa: PLR0911, PLR0912
    """Actualiza parcialmente una penalización existente.

    Permite modificar campos individuales de una penalización. Si se
    cambia el estado a inactivo, se establece la fecha de fin automáticamente.

    Args:
        penalty_id (int): Identificador de la penalización a actualizar.

    Returns:
        tuple: Respuesta JSON con la penalización actualizada y código
            HTTP 200, o un mensaje de error con el código correspondiente.

    Raises:
        mysql.connector.Error: Si ocurre un error de conexión a la BD.

    """
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(penalty_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()
    except Exception:
        data = None

    is_valid, error = valid_penalty_patch(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    if "status" in data:
        data.update({"activa": 1 if data.get("status") == "Activa" else 0})
        data.pop("status")

    if "notes" in data:
        data.update({"motivo": data.get("notes")})
        data.pop("notes")

    keysToUpdate = list(data.keys())
    set_expressions = [f"{f} = %({f})s" for f in keysToUpdate]

    if not data.get("activa", True):
        set_expressions.append("fecha_fin = NOW()")

    set_clause = ", ".join(set_expressions)
    data.update({"penalty_id": penalty_id})

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = f"UPDATE penalizacion SET {set_clause} WHERE id = %(penalty_id)s"
        cursor.execute(sql, data)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        cursor.execute(
            """
            SELECT id,
                   id_usuario,
                   id_reserva,
                   motivo,
                   fecha_inicio,
                   fecha_fin,
                   activa,
                   severity
            FROM penalizacion
            WHERE id = %(penalty_id)s
            """,
            {"penalty_id": penalty_id},
        )

        row = cursor.fetchone()

        if not row:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify(format_penalty(row)), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

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


@penalties_bp.route("/api/penalties", methods=["GET"])
def listar_penalizaciones():
    """Lista todas las penalizaciones del sistema.

    Requiere un JWT válido con rol admin en el request.

    Returns:
        tuple: Respuesta JSON con la lista de todas las penalizaciones
            y código HTTP 200. Retorna 403 si el usuario no es admin.

    """
    penalizaciones = listar_penalizaciones_db()
    return jsonify(penalizaciones), HTTP_OK


@penalties_bp.route("/api/penalties", methods=["POST"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def crear_penalizacion():
    """Crea una nueva penalización para un usuario.

    Requiere un JWT válido con rol admin y un cuerpo JSON con los
    campos 'user_id' y 'reason'.

    Returns:
        tuple: Respuesta JSON con la penalización creada y código
            HTTP 201. Retorna 400 si faltan datos obligatorios,
            o 404 si el usuario no existe.

    """
    datos = request.get_json()

    if not datos or not datos.get("user_id") or not datos.get("reason"):
        return jsonify({"error": "user_id y reason son requeridos"}), HTTP_BAD_REQUEST

    id_usuario = datos["user_id"]
    motivo = datos["reason"]

    if not usuario_existe(id_usuario):
        return jsonify({"error": "Usuario no encontrado"}), HTTP_NOT_FOUND

    id_penalizacion = crear_penalizacion_db(id_usuario, motivo)
    penalizacion = obtener_penalizacion_por_id(id_penalizacion)

    return jsonify(penalizacion), HTTP_CREATED
