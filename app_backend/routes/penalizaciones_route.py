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
from validators import valid_id, valid_penalty_patch, valid_usuario_id_query, valid_penalizaciones_filters
from utiles.autenticacion import requiere_auth
from utiles.formateadores import formatear_penalizaciones
from utiles.servicios import crear_penalizacion_db, existe_reserva, obtener_penalizacion_por_id, usuario_existe

penalizaciones_bp = Blueprint("penalizaciones", __name__)
logger = logging.getLogger(__name__)


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

        return jsonify(formatear_penalizaciones(row)), HTTP_OK

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

        return jsonify(formatear_penalizaciones(row)), HTTP_OK

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

    filters = {
        "usuario": request.args.get("usuario"),
        "estado": request.args.get("estado"),
        "severidad": request.args.get("severidad"),
        "fecha": request.args.get("fecha"),
    }

    is_valid, error, parsed_filters = valid_penalizaciones_filters(filters)

    usuario_id = None
    if "usuario_id" in request.args:
        is_valid, error, usuario_id = valid_usuario_id_query(request.args)
        if not is_valid:
            return jsonify({"error": "Parámetros de consulta inválidos", "detail": error}), HTTP_BAD_REQUEST

    if request.usuario_rol not in ("admin", "bibliotecario"):
        if usuario_id is None or usuario_id != request.usuario_id:
            return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        consulta_penalizaciones = """
            SELECT penalizacion.id, nombre, nombre_art, severidad, motivo, activa, fecha_inicio,
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
                return jsonify({"error": f"Usuario con ID {usuario_id} no encontrado"}), HTTP_NOT_FOUND
            condiciones_where.append("penalizacion.id_usuario = %(usuario_id)s")
            valores["usuario_id"] = usuario_id

        if parsed_filters.get("estado") is not None:
            if parsed_filters["estado"] == "activa":
                valores["activa"] = 1
            else:
                valores["activa"] = 0
            condiciones_where.append("penalizacion.activa = %(activa)s")
        if parsed_filters.get("usuario") is not None:
            condiciones_where.append("usuario.nombre LIKE %(usuario)s")
            valores["usuario"] = f"%{parsed_filters.get('usuario')}%"
        if parsed_filters.get("fecha") is not None:
            condiciones_where.append("DATE(penalizacion.fecha_inicio) = %(fecha)s")
            valores["fecha"] = parsed_filters.get("fecha")
        if parsed_filters["severidad"] is not None:
            condiciones_where.append("penalizacion.severidad = %(severidad)s")
            valores["severidad"] = parsed_filters["severidad"]

        clausula_where = " WHERE " + " AND ".join(condiciones_where) if condiciones_where else ""
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
