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
from validators import valid_id, valid_articulo, valid_articulo_filters, valid_articulo_update

articulos_bp = Blueprint("articulos", __name__)
logger = logging.getLogger(__name__)


def format_articulo(row):
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


@articulos_bp.route("/api/articulos", methods=["GET"])
def get_articulos():
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

    is_valid, error, parsed_filters = valid_articulo_filters(filters)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    where_conditions = ["activo = 1"]
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
        articulos = [format_articulo(row) for row in cursor.fetchall()]

        return jsonify(articulos), HTTP_OK

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


@articulos_bp.route("/api/articulos", methods=["POST"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def create_articulo():
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

    is_valid, error = valid_articulo(data)
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

        articulo_id = cursor.lastrowid
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
            WHERE id = %(articulo_id)s
            """,
            {"articulo_id": articulo_id},
        )
        articulo = cursor.fetchone()

        return jsonify(format_articulo(articulo)), HTTP_CREATED

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


@articulos_bp.route("/api/articulos/<int:articulo_id>", methods=["PUT"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def update_articulo(articulo_id):
    """Actualiza un artículo existente del inventario.

    Recibe el ID del artículo como parámetro de ruta y los campos a
    actualizar en el cuerpo de la petición como JSON.

    Args:
        articulo_id (int): Identificador único del artículo a actualizar.

    Returns:
        tuple: JSON con el artículo actualizado y el código HTTP correspondiente.

    """
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(articulo_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()
    except Exception:
        data = None

    is_valid, error = valid_articulo_update(data)
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
    values["articulo_id"] = articulo_id

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = f"UPDATE articulos SET {set_clause} WHERE id = %(articulo_id)s"
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
            WHERE id = %(articulo_id)s
            """,
            {"articulo_id": articulo_id},
        )
        articulo = cursor.fetchone()

        if not articulo:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify(format_articulo(articulo)), HTTP_OK

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


@articulos_bp.route("/api/articulos/<int:articulo_id>/condition", methods=["PATCH"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def actualizar_condicion(articulo_id):
    """Actualiza la condición o estado de un artículo.

    Recibe el ID del artículo y un JSON con el nuevo estado ('disponible', 'dañado', 'reparacion', 'dado de baja').

    Args:
        articulo_id (int): ID único del artículo a actualizar.

    Returns:
        tuple: JSON con el artículo actualizado y el código HTTP correspondiente.

    """
    if articulo_id <= 0:
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
                "UPDATE articulos SET necesita_reparacion = 1 WHERE id = %s", (articulo_id,)
            )

        elif nuevo_estado == "dado de baja":
            cursor.execute(
                "UPDATE articulos SET stock = 0, necesita_reparacion = 1 WHERE id = %s",
                (articulo_id,),
            )

        else:
            cursor.execute(
                "UPDATE articulos SET necesita_reparacion = 0 WHERE id = %s", (articulo_id,)
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
            (articulo_id,),
        )

        articulo = cursor.fetchone()
        return jsonify(format_articulo(articulo)), HTTP_OK

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        if cursor:
            cursor.close()
        conn.close()


@articulos_bp.route("/api/articulos/<int:articulo_id>", methods=["DELETE"])
@requiere_auth(roles=["admin", "bibliotecario", "profesor"])
def eliminar_articulo(articulo_id):
    """Realiza la baja lógica de un artículo en el inventario.

    Args:
        articulo_id (int): Identificador único del artículo a dar de baja.

    Returns:
        tuple: JSON con mensaje de éxito o error y el código HTTP correspondiente.

    """
    if articulo_id <= 0:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor()

        sql = """
            UPDATE articulos
            SET activo = 0
            WHERE id = %s
        """

        cursor.execute(sql, (articulo_id,))
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


@articulos_bp.route("/api/articulos/<int:articulo_id>", methods=["GET"])
def get_articulo_by_id(articulo_id):
    """Obtiene los datos de un artículo por su identificador.

    Args:
        articulo_id (int): Identificador único del artículo a consultar.

    Returns:
        tuple: JSON con el artículo encontrado y código HTTP 200,
            o un error con su código correspondiente.

    """
    if valid_id(articulo_id) is None:
        return jsonify({"error": "Formato de ID de artículo inválido"}), HTTP_BAD_REQUEST

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
        cursor.execute(query, (articulo_id,))
        articulo = cursor.fetchone()

        if not articulo:
            return jsonify(
                {"error": f"Artículo con ID {articulo_id} no encontrado"}
            ), HTTP_NOT_FOUND

        return jsonify(articulo), HTTP_OK

    except mysql.connector.Error as query_err:

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
