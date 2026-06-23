import logging

import mysql.connector
from flask import Blueprint, jsonify, request

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MSG_DB_CONNECTION_FAILED,
    MSG_DB_QUERY_FAILED,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
)
from paginacion import construir_respuesta_paginada, obtener_parametros_paginacion
from routes.auth_route import requiere_auth

normativas_bp = Blueprint("normativas", __name__, url_prefix="/api/normativas")
logger = logging.getLogger(__name__)


def _revertir_transaccion(conn):
    try:
        conn.rollback()
    except Exception:
        logger.exception("No se pudo revertir la transacción de normativas")


@normativas_bp.route("/", methods=["GET"])
def listar_normativas():
    """Descripción: función listar_normativas."""
    pagination, error = obtener_parametros_paginacion(request.args)
    if error:
        return jsonify({"error": error}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM normativa")
        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT * FROM normativa
            ORDER BY fecha DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            pagination,
        )
        data = cursor.fetchall()

        return (
            jsonify(
                construir_respuesta_paginada(
                    data,
                    total,
                    request,
                    pagination["limit"],
                    pagination["offset"],
                )
            ),
            HTTP_OK,
        )
    except mysql.connector.Error as err:
        logger.error("Error de base de datos al listar normativas: %s", err)
        return jsonify({"error": MSG_DB_QUERY_FAILED}), HTTP_INTERNAL_SERVER_ERROR
    except Exception:
        logger.exception("Error inesperado al listar normativas")
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        conn.close()


@normativas_bp.route("/", methods=["POST"])
@requiere_auth(roles=["admin", "bibliotecario"])
def crear_normativa():
    """Descripción: función crear_normativa."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Faltan datos"}), HTTP_BAD_REQUEST

    titulo = data.get("titulo")
    descripcion = data.get("descripcion")

    if not titulo or not descripcion:
        return jsonify({"error": "Faltan datos"}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO normativa (titulo, descripcion, fecha)
            VALUES (%s, %s, NOW())
        """,
            (titulo, descripcion),
        )

        conn.commit()

        return jsonify({"mensaje": "Normativa creada"}), HTTP_CREATED
    except mysql.connector.Error as err:
        _revertir_transaccion(conn)
        logger.error("Error de base de datos al crear normativa: %s", err)
        return jsonify({"error": MSG_DB_QUERY_FAILED}), HTTP_INTERNAL_SERVER_ERROR
    except Exception:
        _revertir_transaccion(conn)
        logger.exception("Error inesperado al crear normativa")
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        conn.close()


@normativas_bp.route("/<int:id>", methods=["PUT"])
@requiere_auth(roles=["admin", "bibliotecario"])
def editar_normativa(id):
    """Descripción: función editar_normativa."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Faltan datos"}), HTTP_BAD_REQUEST

    titulo = data.get("titulo")
    descripcion = data.get("descripcion")

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE normativa SET titulo = %s, descripcion = %s WHERE id = %s
        """,
            (titulo, descripcion, id),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        conn.commit()

        return jsonify({"mensaje": "Normativa actualizada"}), HTTP_OK
    except mysql.connector.Error as err:
        _revertir_transaccion(conn)
        logger.error("Error de base de datos al editar normativa: %s", err)
        return jsonify({"error": MSG_DB_QUERY_FAILED}), HTTP_INTERNAL_SERVER_ERROR
    except Exception:
        _revertir_transaccion(conn)
        logger.exception("Error inesperado al editar normativa")
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        conn.close()


@normativas_bp.route("/<int:id>", methods=["DELETE"])
@requiere_auth(roles=["admin", "bibliotecario"])
def eliminar_normativa(id):
    """Descripción: función eliminar_normativa."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM normativa WHERE id = %s", (id,))

        if cursor.rowcount == 0:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        conn.commit()

        return jsonify({"mensaje": "Normativa eliminada"}), HTTP_OK
    except mysql.connector.Error as err:
        _revertir_transaccion(conn)
        logger.error("Error de base de datos al eliminar normativa: %s", err)
        return jsonify({"error": MSG_DB_QUERY_FAILED}), HTTP_INTERNAL_SERVER_ERROR
    except Exception:
        _revertir_transaccion(conn)
        logger.exception("Error inesperado al eliminar normativa")
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        conn.close()
