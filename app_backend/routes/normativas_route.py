from flask import Blueprint, jsonify, request

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_OK,
)
from paginacion import construir_respuesta_paginada, obtener_parametros_paginacion
from routes.auth_route import requiere_auth

normativas_bp = Blueprint("normativas", __name__, url_prefix="/api/normativas")


@normativas_bp.route("/", methods=["GET"])
def listar_normativas():
    """Descripción: función listar_normativas."""
    pagination, error = obtener_parametros_paginacion(request.args)
    if error:
        return jsonify({"error": error}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
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

    cursor.close()
    conn.close()

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


@normativas_bp.route("/", methods=["POST"])
@requiere_auth(roles=["admin", "bibliotecario"])
def crear_normativa():
    """Descripción: función crear_normativa."""
    data = request.get_json()
    titulo = data.get("titulo")
    descripcion = data.get("descripcion")

    if not titulo or not descripcion:
        return jsonify({"error": "Faltan datos"}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO normativa (titulo, descripcion, fecha)
        VALUES (%s, %s, NOW())
    """,
        (titulo, descripcion),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Normativa creada"}), HTTP_CREATED


@normativas_bp.route("/<int:id>", methods=["PUT"])
@requiere_auth(roles=["admin", "bibliotecario"])
def editar_normativa(id):
    """Descripción: función editar_normativa."""
    data = request.get_json()
    titulo = data.get("titulo")
    descripcion = data.get("descripcion")

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE normativa SET titulo = %s, descripcion = %s WHERE id = %s
    """,
        (titulo, descripcion, id),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Normativa actualizada"}), HTTP_OK


@normativas_bp.route("/<int:id>", methods=["DELETE"])
@requiere_auth(roles=["admin", "bibliotecario"])
def eliminar_normativa(id):
    """Descripción: función eliminar_normativa."""
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM normativa WHERE id = %s", (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Normativa eliminada"}), HTTP_OK
