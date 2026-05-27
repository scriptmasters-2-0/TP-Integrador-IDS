from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from constants import HTTP_OK, HTTP_NOT_FOUND, HTTP_BAD_REQUEST
from database import obtener_conexion

blueprint_usuarios = Blueprint("usuarios", __name__)


#pre:  id_usuario es un entero positivo.
#post: marca el usuario como inactivo, retorna True si se actualizó, False si no existía.
def desactivar_usuario_db(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("UPDATE usuario SET activo = FALSE WHERE id = %s", (id_usuario,))
    conexion.commit()
    actualizado = cursor.rowcount > 0
    cursor.close()
    conexion.close()
    return actualizado


#pre:  el request incluye un JWT válido con rol admin. id_usuario es un entero positivo.
#post: devuelve 200 si se dio de baja, 404 si no existe, 400 si el ID es inválido.
@blueprint_usuarios.route("/api/usuarios/<int:id_usuario>", methods=["DELETE"])
@jwt_required()
def eliminar_usuario(id_usuario):
    if id_usuario <= 0:
        return jsonify({"error": "ID inválido"}), HTTP_BAD_REQUEST

    if desactivar_usuario_db(id_usuario):
        return jsonify({"mensaje": "Usuario dado de baja con éxito"}), HTTP_OK
    return jsonify({"error": "Usuario no encontrado"}), HTTP_NOT_FOUND