"""Routes for inventory item endpoints."""

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
from validators import valid_id, valid_item, valid_item_filters, valid_item_update

items_bp = Blueprint("items", __name__)


def format_item(row):
    """Format database item rows as API responses."""
    return {
        "id": row.get("id"),
        "nombre_art": row.get("nombre_art"),
        "tipo": row.get("tipo"),
        "seccion": row.get("seccion"),
        "prestacion_maxima": row.get("prestacion_maxima"),
        "stock": row.get("stock"),
        "necesita_reparacion": bool(row.get("necesita_reparacion")),
    }


@items_bp.route("/api/items", methods=["GET"])
def get_items():  # noqa: PLR0912
    """Return inventory items, optionally filtered by query parameters."""
    filters = {
        "tipo": request.args.get("tipo"),
        "seccion": request.args.get("seccion"),
        "disponible": request.args.get("disponible"),
        "necesita_reparacion": request.args.get("necesita_reparacion"),
    }

    is_valid, error, parsed_filters = valid_item_filters(filters)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    where_conditions = []
    values = {}

    if parsed_filters.get("tipo") is not None:
        where_conditions.append("tipo = %(tipo)s")
        values["tipo"] = parsed_filters.get("tipo")

    if parsed_filters.get("seccion") is not None:
        where_conditions.append("seccion = %(seccion)s")
        values["seccion"] = parsed_filters.get("seccion")

    if parsed_filters.get("disponible") is not None:
        if parsed_filters.get("disponible"):
            where_conditions.append("stock > 0")
            where_conditions.append("necesita_reparacion = 0")
        else:
            where_conditions.append("(stock <= 0 OR necesita_reparacion = 1)")

    if parsed_filters.get("necesita_reparacion") is not None:
        where_conditions.append("necesita_reparacion = %(necesita_reparacion)s")
        values["necesita_reparacion"] = parsed_filters.get("necesita_reparacion")

    sql = """
        SELECT id,
               nombre_art,
               tipo,
               seccion,
               prestacion_maxima,
               stock,
               necesita_reparacion
        FROM articulos
    """

    if where_conditions:
        sql += " WHERE " + " AND ".join(where_conditions)

    sql += " ORDER BY id"

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, values)
        items = [format_item(row) for row in cursor.fetchall()]

        return jsonify(items), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
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


@items_bp.route("/api/items", methods=["POST"])
def create_item():
    """Create a new inventory item."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    try:
        data = request.get_json()
    except Exception:
        data = None

    is_valid, error = valid_item(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    values = {
        "nombre_art": data.get("nombre_art"),
        "tipo": data.get("tipo"),
        "seccion": data.get("seccion"),
        "prestacion_maxima": int(data.get("prestacion_maxima")),
        "stock": int(data.get("stock")) if data.get("stock") is not None else 1,
        "necesita_reparacion": 1 if data.get("necesita_reparacion") else 0,
    }

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            INSERT INTO articulos
                (nombre_art,
                 tipo,
                 seccion,
                 prestacion_maxima,
                 stock,
                 necesita_reparacion)
            VALUES
                (%(nombre_art)s,
                 %(tipo)s,
                 %(seccion)s,
                 %(prestacion_maxima)s,
                 %(stock)s,
                 %(necesita_reparacion)s)
        """
        cursor.execute(sql, values)
        conn.commit()

        item_id = cursor.lastrowid
        cursor.execute(
            """
            SELECT id,
                   nombre_art,
                   tipo,
                   seccion,
                   prestacion_maxima,
                   stock,
                   necesita_reparacion
            FROM articulos
            WHERE id = %(item_id)s
            """,
            {"item_id": item_id},
        )
        item = cursor.fetchone()

        return jsonify(format_item(item)), HTTP_CREATED

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
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


@items_bp.route("/api/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):  # noqa: PLR0911, PLR0912
    """Update an existing inventory item."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(item_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()
    except Exception:
        data = None

    is_valid, error = valid_item_update(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    values = {}
    for field in data:
        if field in ("prestacion_maxima", "stock"):
            values[field] = int(data.get(field))
        elif field == "necesita_reparacion":
            values[field] = 1 if data.get(field) else 0
        else:
            values[field] = data.get(field)

    set_clause = ", ".join([f"{field} = %({field})s" for field in values])
    values["item_id"] = item_id

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = f"UPDATE articulos SET {set_clause} WHERE id = %(item_id)s"
        cursor.execute(sql, values)
        conn.commit()

        cursor.execute(
            """
            SELECT id,
                   nombre_art,
                   tipo,
                   seccion,
                   prestacion_maxima,
                   stock,
                   necesita_reparacion
            FROM articulos
            WHERE id = %(item_id)s
            """,
            {"item_id": item_id},
        )
        item = cursor.fetchone()

        if not item:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify(format_item(item)), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
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
