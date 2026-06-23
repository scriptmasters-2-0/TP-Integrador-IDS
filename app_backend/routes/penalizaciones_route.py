"""Rutas de la API para la gestión de penalizaciones.

Define los endpoints para consultar, crear y actualizar penalizaciones
de usuarios en el sistema.
"""

import logging

import mysql.connector
from flask import Blueprint, jsonify, request

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_FORBIDDEN,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MSG_BAD_REQUEST,
    MSG_DB_CONNECTION_FAILED,
    MSG_FORBIDDEN,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
)
from paginacion import construir_respuesta_paginada, obtener_parametros_paginacion
from routes.auth_route import requiere_auth
from validators import valid_id, valid_penalty_patch, valid_usuario_id_query

penalizaciones_bp = Blueprint("penalizaciones", __name__)
logger = logging.getLogger(__name__)


def usuario_existe(id_usuario):
    """Verifica si un usuario existe en la base de datos.

    Args:
        id_usuario (int): Identificador del usuario a verificar.

    Returns:
        tuple: Existencia del usuario y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return False, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM usuario WHERE id = %s", (id_usuario,))
        return cursor.fetchone() is not None, None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def existe_reserva(id_reserva):
    """Verifica si una reserva existe en la base de datos.

    Args:
        id_reserva (int): Identificador de la reserva a verificar.

    Returns:
        tuple: Existencia de la reserva y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return False, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM reserva WHERE id = %s", (id_reserva,))
        return cursor.fetchone() is not None, None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def listar_penalizaciones_db():
    """Obtiene todas las penalizaciones de la base de datos.

    Returns:
        tuple: Lista de penalizaciones y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM penalizacion")
        return cursor.fetchall(), None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def crear_penalizacion_db(id_usuario, motivo, severidad="media", id_reserva=None):
    """Inserta una nueva penalización activa en la base de datos.

    Crea una penalización con duración de 15 días a partir de la
    fecha actual.

    Args:
        id_usuario (int): Identificador del usuario a penalizar.
            Debe ser un entero positivo.
        motivo (str): Motivo de la penalización. No debe estar vacío.
        severidad (str): Severidad de la penalización ('baja', 'media', 'alta').
            Por defecto 'media'.
        id_reserva (int): Identificador opcional de la reserva asociada.

    Returns:
        tuple: Identificador generado y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO penalizacion (id_usuario, id_reserva, motivo, fecha_inicio, fecha_fin, activa, severidad)
            VALUES (%s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 15 DAY), TRUE, %s)
            """,
            (id_usuario, id_reserva, motivo, severidad),
        )
        conexion.commit()
        return cursor.lastrowid, None
    except mysql.connector.Error as err:
        logger.error("Error de base de datos al crear penalización: %s", err)
        return None, MSG_INTERNAL_SERVER_ERROR
    except Exception:
        logger.exception("Error inesperado al crear penalización")
        return None, MSG_INTERNAL_SERVER_ERROR
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass

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
        "usuarioId": row.get("id_usuario"),
        "reservaId": row.get("id_reserva"),
        "reason": row.get("motivo"),
        "status": "Activa" if row.get("activa") else "Levantada",
        "severidad": row.get("severidad"),
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
        tuple: Penalización encontrada y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM penalizacion WHERE id = %s", (id_penalizacion,))
        return cursor.fetchone(), None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


@penalizaciones_bp.route("/api/penalizaciones/<int:penalty_id>", methods=["GET"])
@requiere_auth(roles=["admin", "bibliotecario"])
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
                   severidad
            FROM penalizacion
            WHERE id = %(penalty_id)s
            """,
            {"penalty_id": penalty_id},
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

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


@penalizaciones_bp.route("/api/penalizaciones/<int:penalty_id>", methods=["PATCH"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def patch_penalty(penalty_id):
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
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        cursor.execute(
            """
            SELECT id,
                   id_usuario,
                   id_reserva,
                   motivo,
                   fecha_inicio,
                   fecha_fin,
                   activa,
                   severidad
            FROM penalizacion
            WHERE id = %(penalty_id)s
            """,
            {"penalty_id": penalty_id},
        )

        row = cursor.fetchone()

        if not row:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

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


@penalizaciones_bp.route("/api/penalizaciones", methods=["GET"])
@requiere_auth(roles=["admin", "bibliotecario", "alumno", "profesor"])
def listar_penalizaciones():
    """Obtiene penalizaciones asociadas a un usuario mediante query param.
    o Lista todas las penalizaciones del sistema si no se especifica usuario_id.
    Admin y bibliotecario pueden listar todas. Alumno y profesor solo
    pueden consultar las penalizaciones propias.

    Query Params:
        usuario_id (str): Identificador del usuario a consultar.

    Returns:
        tuple: Respuesta JSON con la lista de todas las penalizaciones
            y código HTTP 200. Retorna 403 si el usuario no es admin.

    """
    pagination, error = obtener_parametros_paginacion(request.args)
    if error:
        return jsonify({"error": error}), HTTP_BAD_REQUEST

    nombre_usuario = request.args.get("usuario")
    usuario_id = None
    if "usuario_id" in request.args:
        is_valid, error, usuario_id = valid_usuario_id_query(request.args)
        if not is_valid:
            return jsonify(
                {"error": "Parámetros de consulta inválidos", "detail": error}
            ), HTTP_BAD_REQUEST

    if request.usuario_rol not in ("admin", "bibliotecario"):
        if usuario_id is None or usuario_id != request.usuario_id:
            return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        consulta_penalizaciones = """SELECT penalizacion.id, nombre, nombre_art, severidad, motivo, activa, fecha_inicio,
            DATE_FORMAT(fecha_fin, '%d/%m/%y') as fecha_fin, DATEDIFF(CURDATE(), fecha_fin) as retraso
            FROM penalizacion
            INNER JOIN usuario ON penalizacion.id_usuario = usuario.id
            LEFT JOIN reserva ON penalizacion.id_reserva = reserva.id
            LEFT JOIN articulos ON reserva.id_reservado = articulos.id
            """
        consulta_total_penalizaciones = """SELECT COUNT(*) AS total
            FROM penalizacion
            INNER JOIN usuario ON penalizacion.id_usuario = usuario.id
            LEFT JOIN reserva ON penalizacion.id_reserva = reserva.id
            LEFT JOIN articulos ON reserva.id_reservado = articulos.id
            """
        condiciones_where = []
        valores = {}

        if usuario_id:
            consulta_usuario = "SELECT id FROM usuario WHERE id = %s"
            cursor.execute(consulta_usuario, (usuario_id,))
            usuario_existe_db = cursor.fetchone()

            if not usuario_existe_db:
                return jsonify(
                    {"error": f"Usuario con ID {usuario_id} no encontrado"}
                ), HTTP_NOT_FOUND
            condiciones_where.append("penalizacion.id_usuario = %(usuario_id)s")
            valores["usuario_id"] = usuario_id

        if nombre_usuario:
            condiciones_where.append("usuario.nombre LIKE %(nombre_usuario)s")
            valores["nombre_usuario"] = f"%{nombre_usuario}%"

        clausula_where = (
            " WHERE " + " AND ".join(condiciones_where)
            if condiciones_where
            else ""
        )
        cursor.execute(consulta_total_penalizaciones + clausula_where, valores)
        total = cursor.fetchone()["total"]

        consulta_paginada = (
            consulta_penalizaciones
            + clausula_where
            + """
            ORDER BY penalizacion.fecha_inicio DESC, penalizacion.id DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """
        )
        cursor.execute(consulta_paginada, {**valores, **pagination})
        penalizaciones = cursor.fetchall()

        return (
            jsonify(
                construir_respuesta_paginada(
                    penalizaciones,
                    total,
                    request,
                    pagination["limit"],
                    pagination["offset"],
                )
            ),
            HTTP_OK,
        )

    except mysql.connector.Error as query_err:
        logger.error("Error en la consulta a la base de datos: %s", query_err)

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


@penalizaciones_bp.route("/api/penalizaciones", methods=["POST"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def crear_penalizacion():
    """Crea una nueva penalización para un usuario.

    Requiere un JWT válido con rol admin, bibliotecario o profesor y un
    cuerpo JSON con los campos 'usuario_id' y 'reason'. Opcionalmente
    'severidad' ('baja', 'media', 'alta'; por defecto 'media').

    Returns:
        tuple: Respuesta JSON con la penalización creada y código
            HTTP 201. Retorna 400 si faltan datos obligatorios o si
            la severidad es inválida, o 404 si el usuario no existe.

    """
    datos = request.get_json()

    if not datos or not datos.get("usuario_id") or not datos.get("reason"):
        return jsonify({"error": "usuario_id y reason son requeridos"}), HTTP_BAD_REQUEST

    id_usuario = datos["usuario_id"]
    motivo = datos["reason"]
    severidad = datos.get("severidad", "media")
    id_reserva = None

    if "id_reserva" in datos:
        id_reserva = valid_id(datos.get("id_reserva"))
        if id_reserva is None:
            return jsonify({"error": "id_reserva inválido"}), HTTP_BAD_REQUEST
        reserva_encontrada, error = existe_reserva(id_reserva)
        if error:
            return jsonify({"error": error}), HTTP_INTERNAL_SERVER_ERROR
        if not reserva_encontrada:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

    if severidad not in ("baja", "media", "alta"):
        return jsonify({"error": "severidad inválida"}), HTTP_BAD_REQUEST

    existe_usuario, error = usuario_existe(id_usuario)
    if error:
        return jsonify({"error": error}), HTTP_INTERNAL_SERVER_ERROR

    if not existe_usuario:
        return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

    id_penalizacion, error = crear_penalizacion_db(
        id_usuario,
        motivo,
        severidad,
        id_reserva=id_reserva,
    )
    if error:
        return jsonify({"error": error}), HTTP_INTERNAL_SERVER_ERROR

    penalizacion, error = obtener_penalizacion_por_id(id_penalizacion)
    if error:
        return jsonify({"error": error}), HTTP_INTERNAL_SERVER_ERROR

    return jsonify(penalizacion), HTTP_CREATED
