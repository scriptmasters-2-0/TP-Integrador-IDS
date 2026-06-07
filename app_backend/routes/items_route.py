"""Rutas para los endpoints de artículos del inventario."""

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
    MSG_BAD_REQUEST,
    MSG_DB_CONNECTION_FAILED,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
)
from routes.auth_route import requiere_auth
from validators import valid_id, valid_item, valid_item_filters, valid_item_update

items_bp = Blueprint("items", __name__)


def format_item(row):
    """Formatea una fila de artículo de la base de datos como respuesta de la API.

    Args:
        row (dict): Diccionario con los datos del artículo obtenidos de la
            base de datos.

    Returns:
        dict: Diccionario formateado con los campos del artículo para la respuesta.

    """
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
    """Retorna artículos del inventario, opcionalmente filtrados por query.

    Los filtros disponibles son: tipo, sección, disponibilidad y
    necesidad de reparación. Se envían como query parameters.

    Returns:
        tuple: JSON con la lista de artículos y el código HTTP correspondiente.

    """
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
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def create_item():
    """Crea un nuevo artículo en el inventario.

    Recibe los datos del artículo en el cuerpo de la petición como JSON,
    lo valida, lo inserta en la base de datos y retorna el artículo creado.

    Returns:
        tuple: JSON con el artículo creado y el código HTTP 201, o un error.

    """
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
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def update_item(item_id):  # noqa: PLR0911, PLR0912
    """Actualiza un artículo existente del inventario.

    Recibe el ID del artículo como parámetro de ruta y los campos a
    actualizar en el cuerpo de la petición como JSON.

    Args:
        item_id (int): Identificador único del artículo a actualizar.

    Returns:
        tuple: JSON con el artículo actualizado y el código HTTP correspondiente.

    """
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


@items_bp.route("/api/items/<int:item_id>/condition", methods=["PATCH"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def actualizar_condicion(item_id):
    """Actualiza la condición o estado de un artículo.

    Recibe el ID del artículo y un JSON con el nuevo estado ('disponible', 'dañado', 'reparacion', 'dado de baja').

    Args:
        item_id (int): ID único del artículo a actualizar.

    Returns:
        tuple: JSON con el artículo actualizado y el código HTTP correspondiente.

    """
    if item_id <= 0:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()
        nuevo_estado = data.get("estado")

    except Exception:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    estados_validos = ["disponible", "dañado", "reparacion", "dado de baja"]

    if nuevo_estado not in estados_validos:
        return jsonify(
            {"error": MSG_BAD_REQUEST, "detail": "Estado no permitido"}
        ), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        if nuevo_estado in ["reparacion", "dañado"]:
            cursor.execute(
                "UPDATE articulos SET necesita_reparacion = 1 WHERE id = %s", (item_id,)
            )

        elif nuevo_estado == "dado de baja":
            cursor.execute(
                "UPDATE articulos SET stock = 0, necesita_reparacion = 1 WHERE id = %s",
                (item_id,),
            )

        else:
            cursor.execute(
                "UPDATE articulos SET necesita_reparacion = 0 WHERE id = %s", (item_id,)
            )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        cursor.execute(
            """
            SELECT id, nombre_art, tipo, seccion, prestacion_maxima, stock, necesita_reparacion
            FROM articulos
            WHERE id = %s
        """,
            (item_id,),
        )

        item = cursor.fetchone()
        return jsonify(format_item(item)), HTTP_OK

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        if cursor:
            cursor.close()
        conn.close()


@items_bp.route("/api/items/<int:item_id>", methods=["DELETE"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def eliminar_item(item_id):
    """Realiza la baja lógica de un artículo en el inventario.

    Args:
        item_id (int): Identificador único del artículo a dar de baja.

    Returns:
        tuple: JSON con mensaje de éxito o error y el código HTTP correspondiente.

    """
    if item_id <= 0:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor()

        sql = """
            UPDATE articulos
            SET stock = 0, necesita_reparacion = 1
            WHERE id = %s
        """

        cursor.execute(sql, (item_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify({"mensaje": "Artículo dado de baja con éxito"}), HTTP_OK

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        if cursor:
            cursor.close()
        conn.close()


@items_bp.route("/api/items/<int:item_id>", methods=["GET"])
def get_item_by_id(item_id):
    """Obtiene los datos de un artículo por su identificador.

    Args:
        item_id (int): Identificador único del artículo a consultar.

    Returns:
        tuple: JSON con el artículo encontrado y código HTTP 200,
            o un error con su código correspondiente.

    """
    if valid_id(item_id) is None:
        return jsonify({"error": "Invalid item ID format"}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        query = (
            "SELECT id, nombre_art, tipo, seccion, prestacion_maxima, stock, necesita_reparacion "
            "FROM articulos WHERE id = %s"
        )
        cursor.execute(query, (item_id,))
        item = cursor.fetchone()

        if not item:
            return jsonify(
                {"error": f"Item with ID {item_id} not found"}
            ), HTTP_NOT_FOUND

        return jsonify(item), HTTP_OK

    except mysql.connector.Error as query_err:
        logging.error(f"Database query error in get_item_by_id: {query_err}")

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
