"""Rutas para los endpoints de préstamos."""

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
from routes.auth_route import requiere_auth
from validators import valid_id, valid_reserva_create, valid_reserva_status_update

reservas_bp = Blueprint("reservas", __name__)
logger = logging.getLogger(__name__)
ESTADOS_LIBERAN_STOCK = {"cancelado", "rechazado", "devuelto"}


def _debe_liberar_stock(estado_actual, nuevo_estado):
    return (
        estado_actual not in ESTADOS_LIBERAN_STOCK
        and nuevo_estado in ESTADOS_LIBERAN_STOCK
    )


def _debe_consumir_stock(estado_actual, nuevo_estado):
    return (
        estado_actual in ESTADOS_LIBERAN_STOCK
        and nuevo_estado not in ESTADOS_LIBERAN_STOCK
    )


def _sumar_stock(cursor, articulo_id):
    cursor.execute(
        """
        UPDATE articulos
        SET stock = stock + 1
        WHERE id = %(articulo_id)s
        """,
        {"articulo_id": articulo_id},
    )


def _restar_stock_si_hay(cursor, articulo_id):
    cursor.execute(
        """
        UPDATE articulos
        SET stock = stock - 1
        WHERE id = %(articulo_id)s
          AND stock > 0
        """,
        {"articulo_id": articulo_id},
    )
    return cursor.rowcount > 0


def _ajustar_stock_reserva(cursor, estado_actual, articulo_id, nuevo_estado):
    if _debe_liberar_stock(estado_actual, nuevo_estado):
        _sumar_stock(cursor, articulo_id)
        return True, None
    if _debe_consumir_stock(estado_actual, nuevo_estado):
        if not _restar_stock_si_hay(cursor, articulo_id):
            return False, "stock_insuficiente"
    return True, None


def _revertir_transaccion(conn):
    try:
        conn.rollback()
    except Exception:
        logger.exception("No se pudo revertir la transacción")


def format_reserva(row):
    """Formatea una fila de préstamo de la base de datos como respuesta de la API.

    Convierte los campos de fecha a formato ISO 8601 cuando están presentes.

    Args:
        row (dict): Diccionario con los datos del préstamo obtenidos de la
            base de datos.

    Returns:
        dict: Diccionario formateado con los campos del préstamo para la respuesta.

    """
    return {
        "id": row.get("id"),
        "id_usuario": row.get("id_usuario"),
        "usuario_nombre": row.get("usuario_nombre"),
        "id_reservado": row.get("id_reservado"),
        "nombre_art": row.get("nombre_art"),
        "estado_reserva": row.get("estado_reserva"),
        "fecha_retiro": (
            row.get("fecha_retiro").isoformat() if row.get("fecha_retiro") else None
        ),
        "fecha_regreso": (
            row.get("fecha_regreso").isoformat() if row.get("fecha_regreso") else None
        ),
    }


@reservas_bp.route("/api/reservas", methods=["GET"])
@requiere_auth(roles=["admin", "profesor", "bibliotecario", "alumno"])
def listar_reservas():
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        es_admin = request.usuario_rol in ("admin", "bibliotecario")

        if es_admin:
            estado = request.args.get("estado")
            usuario_id = request.args.get("usuario")
            fecha = request.args.get("fecha")

            query = """
                SELECT r.id, r.id_usuario, u.nombre AS usuario_nombre,
                       r.id_reservado, a.nombre_art,
                       r.estado_reserva, r.fecha_retiro, r.fecha_regreso
                FROM reserva r
                JOIN articulos a ON r.id_reservado = a.id
                JOIN usuario u ON r.id_usuario = u.id
                WHERE 1=1
            """
            params = {}
            if estado:
                query += " AND r.estado_reserva = %(estado)s"
                params["estado"] = estado
            if usuario_id:
                query += " AND r.id_usuario = %(usuario_id)s"
                params["usuario_id"] = usuario_id
            if fecha:
                query += " AND DATE(r.fecha_retiro) = %(fecha)s"
                params["fecha"] = fecha

            query += " ORDER BY r.fecha_retiro DESC"
            cursor.execute(query, params)
        else:
            cursor.execute("""
                SELECT r.id, r.id_usuario, u.nombre AS usuario_nombre,
                       r.id_reservado, a.nombre_art,
                       r.estado_reserva, r.fecha_retiro, r.fecha_regreso
                FROM reserva r
                JOIN articulos a ON r.id_reservado = a.id
                JOIN usuario u ON r.id_usuario = u.id
                WHERE r.id_usuario = %(usuario_id)s
                ORDER BY r.fecha_retiro DESC
            """, {"usuario_id": request.usuario_id})

        reservas = [format_reserva(row) for row in cursor.fetchall()]
        return jsonify(reservas), HTTP_OK

    except Exception:
        logger.exception("Error al listar reservas")
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



def obtener_detalle_reserva_db(reserva_id):
    """Obtiene el detalle completo de un préstamo.

    Args:
        reserva_id (int): Identificador único del préstamo a consultar.

    Returns:
        tuple: Reserva encontrada y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                reserva.id,
                reserva.id_usuario,
                reserva.id_reservado,
                usuario.nombre,
                articulos.nombre_art,
                reserva.estado_reserva,
                reserva.fecha_retiro,
                reserva.fecha_regreso
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            WHERE reserva.id = %s
            """,
            (reserva_id,),
        )

        reserva = None

        for fila in cursor:
            reserva = fila

        return reserva, None
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


@reservas_bp.route("/api/reservas/<int:reserva_id>/status", methods=["PATCH"])
@requiere_auth(roles=["admin", "profesor", "bibliotecario", "alumno"])
def patch_reserva_status(reserva_id):
    """Actualiza el estado de un préstamo.

    Recibe el ID del préstamo como parámetro de ruta y el nuevo estado
    en el cuerpo de la petición como JSON.

    Args:
        reserva_id (int): Identificador único del préstamo a actualizar.

    Returns:
        tuple: JSON con el préstamo actualizado y el código HTTP correspondiente.

    """
    if valid_id(reserva_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()
    except Exception:
        data = None

    is_valid, error = valid_reserva_status_update(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id,
                   id_usuario,
                   id_reservado,
                   estado_reserva,
                   fecha_retiro,
                   fecha_regreso
            FROM reserva
            WHERE id = %(reserva_id)s
            """,
            {"reserva_id": reserva_id},
        )
        reserva_actual = cursor.fetchone()

        if not reserva_actual:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        nuevo_estado = data.get("estado_reserva")
        if request.usuario_rol in ("alumno", "profesor"):
            if data.get("estado_reserva") != "cancelado":
                return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN

            if reserva_actual.get("id_usuario") != request.usuario_id:
                return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN

            if reserva_actual.get("estado_reserva") != "pendiente":
                return (
                    jsonify({"error": MSG_BAD_REQUEST, "detail": "reserva_not_pending"}),
                    HTTP_BAD_REQUEST,
                )

        stock_ok, stock_error = _ajustar_stock_reserva(
            cursor,
            reserva_actual.get("estado_reserva"),
            reserva_actual.get("id_reservado"),
            nuevo_estado,
        )
        if not stock_ok:
            _revertir_transaccion(conn)
            return (
                jsonify({"error": MSG_BAD_REQUEST, "detail": stock_error}),
                HTTP_BAD_REQUEST,
            )

        cursor.execute(
            """
            UPDATE reserva
            SET estado_reserva = %(estado_reserva)s
            WHERE id = %(reserva_id)s
            """,
            {
                "estado_reserva": nuevo_estado,
                "reserva_id": reserva_id,
            },
        )

        conn.commit()

        cursor.execute(
            """
            SELECT id,
                   id_usuario,
                   id_reservado,
                   estado_reserva,
                   fecha_retiro,
                   fecha_regreso
            FROM reserva
            WHERE id = %(reserva_id)s
            """,
            {"reserva_id": reserva_id},
        )
        reserva = cursor.fetchone()

        if not reserva:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify(format_reserva(reserva)), HTTP_OK

    except mysql.connector.Error:
        _revertir_transaccion(conn)
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        _revertir_transaccion(conn)
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


@reservas_bp.route("/api/reservas/solicitudes", methods=["GET"])
@requiere_auth(roles=["bibliotecario"])
def listar_solicitudes():
    """Muestra las solicitudes de reserva en estado pendiente"""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR
    
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                r.id, r.id_usuario, u.nombre, a.nombre_art, r.estado_reserva 
            FROM reserva r
            JOIN usuario u
                ON r.id_usuario = u.id
            JOIN articulos a
                ON r.id_reservado = a.id
            WHERE r.estado_reserva = 'pendiente'
            ORDER BY fecha_retiro DESC
        """)

        solicitudes = cursor.fetchall()
        return jsonify(solicitudes), HTTP_OK

    except Exception:
        logger.exception("Error al listar solicitudes de reserva")
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


@reservas_bp.route("/api/reservas", methods=["POST"])
@requiere_auth(roles=["admin", "profesor", "bibliotecario", "alumno"])
def crear_reserva():
    """Crea una nueva reserva para un usuario."""
    try:
        data = request.get_json()
    except Exception:
        data = None

    if not data:
        return jsonify({"error": "Datos de reserva inválidos"}), HTTP_BAD_REQUEST

    is_valid, error, parsed = valid_reserva_create(data)
    if not is_valid:
        return jsonify(
            {"error": "Datos de reserva inválidos", "detail": error}
        ), HTTP_BAD_REQUEST

    usuario_id = parsed.get("usuario_id")
    articulo_id = parsed.get("articulo_id")
    fecha_retiro = parsed.get("fecha_retiro")
    hora_regreso = parsed.get("hora_regreso")

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
        cursor.execute("SELECT id FROM usuario WHERE id = %s", (usuario_id,))
        if not cursor.fetchone():
            return jsonify(
                {"error": f"No se puede crear la reserva. El usuario con ID {usuario_id} no existe"}
            ), HTTP_NOT_FOUND

        cursor.execute(
            "SELECT id, stock, necesita_reparacion FROM articulos WHERE id = %s",
            (articulo_id,),
        )
        articulo = cursor.fetchone()
        if not articulo:
            return jsonify(
                {"error": f"No se puede crear la reserva. El artículo con ID {articulo_id} no existe"}
            ), HTTP_NOT_FOUND

        if articulo["stock"] <= 0 or articulo["necesita_reparacion"]:
            return jsonify(
                {"error": f"El artículo con ID {articulo_id} no está disponible"}
            ), HTTP_BAD_REQUEST

        if fecha_retiro and hora_regreso:
            insert_query = (
                "INSERT INTO reserva (id_usuario, id_reservado, estado_reserva, fecha_retiro, fecha_regreso) "
                "VALUES (%(usuario_id)s, %(articulo_id)s, 'pendiente', %(fecha_retiro)s, "
                "TIMESTAMP(DATE_ADD(DATE(%(fecha_retiro)s), INTERVAL 7 DAY), %(hora_regreso)s))"
            )
            cursor.execute(
                insert_query,
                {
                    "usuario_id": usuario_id,
                    "articulo_id": articulo_id,
                    "fecha_retiro": fecha_retiro,
                    "hora_regreso": hora_regreso,
                },
            )
        else:
            insert_query = (
                "INSERT INTO reserva (id_usuario, id_reservado, estado_reserva, fecha_retiro, fecha_regreso) "
                "VALUES (%s, %s, 'pendiente', NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY))"
            )
            cursor.execute(insert_query, (usuario_id, articulo_id))
        new_reserva_id = cursor.lastrowid
        if not _restar_stock_si_hay(cursor, articulo_id):
            _revertir_transaccion(conn)
            return jsonify(
                {"error": f"El artículo con ID {articulo_id} no está disponible"}
            ), HTTP_BAD_REQUEST
        conn.commit()

        return jsonify(
            {
                "message": "Reserva creada correctamente",
                "reserva_id": new_reserva_id,
                "usuario_id": usuario_id,
                "articulo_id": articulo_id,
            }
        ), HTTP_CREATED

    except mysql.connector.Error:
        _revertir_transaccion(conn)
        logger.exception("Error de base de datos al crear reserva")
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        _revertir_transaccion(conn)
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


@reservas_bp.route("/api/reservas/<int:reserva_id>", methods=["GET"])
@requiere_auth(roles=["admin", "profesor", "bibliotecario", "alumno"])
def obtener_detalle_reserva(reserva_id):
    """Obtiene el detalle completo de una reserva.

    Args:
        reserva_id (int): Identificador único de la reserva a consultar.

    Returns:
        tuple: JSON con el detalle de la reserva y el código HTTP correspondiente.

    """
    if reserva_id <= 0:
        return jsonify({"error": "ID inválido"}), HTTP_BAD_REQUEST

    resultado, error = obtener_detalle_reserva_db(reserva_id)
    if error:
        return jsonify({"error": error}), HTTP_INTERNAL_SERVER_ERROR

    if resultado is not None:
        if (
            request.usuario_rol not in ("admin", "bibliotecario")
            and resultado.get("id_usuario") != request.usuario_id
        ):
            return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN

        return jsonify(resultado), HTTP_OK

    else:
        return jsonify({"error": "Reserva no encontrada"}), HTTP_NOT_FOUND


@reservas_bp.route("/api/reservas/<int:reserva_id>/scan", methods=["PATCH"])
@requiere_auth(roles=["bibliotecario"])
def escanear_qr(reserva_id):
    """Cambia el estado de la reserva (entregado/devuelto) al escanearel qr con una sesion abierta en bibliotecario"""

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_reservado, estado_reserva
            FROM reserva
            WHERE id = %(id)s
        """, {"id": reserva_id})

        reserva = cursor.fetchone()

        if reserva is None:
            return jsonify({"error": "Reserva no encontrada"}), HTTP_NOT_FOUND
        
        if reserva["estado_reserva"] == "aprobado":
            nuevo_estado = "entregado"
        elif reserva["estado_reserva"]  == "entregado":
            nuevo_estado = "devuelto"
        else:
            return jsonify({"error": "Escaneo inválido"}), HTTP_BAD_REQUEST
        
        stock_ok, stock_error = _ajustar_stock_reserva(
            cursor,
            reserva.get("estado_reserva"),
            reserva.get("id_reservado"),
            nuevo_estado,
        )
        if not stock_ok:
            _revertir_transaccion(conn)
            return (
                jsonify({"error": MSG_BAD_REQUEST, "detail": stock_error}),
                HTTP_BAD_REQUEST,
            )

        cursor.execute("""
            UPDATE reserva
            SET estado_reserva = %(estado)s
            WHERE id = %(id)s
        """, {"estado": nuevo_estado, "id": reserva_id})

        conn.commit()

        return jsonify({"reserva_id": reserva_id, "estado_reserva": nuevo_estado}), HTTP_OK

    except Exception:
        _revertir_transaccion(conn)
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
