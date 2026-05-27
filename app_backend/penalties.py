from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from constants import HTTP_OK, HTTP_CREATED, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_FORBIDDEN
from database import obtener_conexion  

blueprint_penalizaciones = Blueprint("penalizaciones", __name__)


#pre: -
#post: devuelve True si el usuario existe en la BD, False caso contrario
def usuario_existe(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM usuario WHERE id = %s", (id_usuario,))
    existe = cursor.fetchone() is not None
    cursor.close()
    conexion.close()
    return existe


#pre:-
#post: devuelve una lista de diccionarios con todas las penalizaciones de la BD.
def listar_penalizaciones_db():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM penalizacion")
    penalizaciones = cursor.fetchall()
    cursor.close()
    conexion.close()
    return penalizaciones


#pre:  id_usuario es entero positivo, motivo es string no vacío.
#post: inserta una penalización activa por 15 días y retorna el ID generado.
def crear_penalizacion_db(id_usuario, motivo):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO penalizacion (id_usuario, motivo, fecha_inicio, fecha_fin, activa)
        VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 15 DAY), TRUE)
        """,
        (id_usuario, motivo)
    )
    conexion.commit()
    id_generado = cursor.lastrowid
    cursor.close()
    conexion.close()
    return id_generado


#pre:  -
#post: devuelve un diccionario con los datos de la penalización si existe, None si no.
def obtener_penalizacion_por_id(id_penalizacion):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM penalizacion WHERE id = %s", (id_penalizacion,))
    penalizacion = cursor.fetchone()
    cursor.close()
    conexion.close()
    return penalizacion


#pre:  el request incluye un JWT válido con rol admin.
#post: retorna 200 con lista de todas las penalizaciones, 403 si no es admin.
@blueprint_penalizaciones.route("/api/penalties", methods=["GET"])
@jwt_required()
def listar_penalizaciones():
    penalizaciones = listar_penalizaciones_db()
    return jsonify(penalizaciones), HTTP_OK


#pre:  el request incluye un JWT válido con rol admin y body con 'user_id' y 'reason'.
#post: retorna 201 con la penalización creada, 400 si faltan datos, 404 si el usuario no existe.
@blueprint_penalizaciones.route("/api/penalties", methods=["POST"])
@jwt_required()
def crear_penalizacion():
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