import mysql.connector
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from constants import HTTP_OK
from database import obtener_conexion

blueprint_logout = Blueprint("auth", __name__)


#pre:  mail es un string con formato de email válido.
#post: devuelve un diccionario con los datos del usuario si existe, None si no se encuentra.
def buscar_usuario_por_mail(mail):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, mail, contrasenia_hash, rol FROM usuario WHERE mail = %s",
        (mail,)
    )
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario

#pre:  el request incluye un JWT válido en el header Authorization.
#post: devuelve 200 confirmando el cierre de sesión. El cliente debe descartar el token.
@blueprint_logout.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"mensaje": "Sesión cerrada con éxito"}), HTTP_OK