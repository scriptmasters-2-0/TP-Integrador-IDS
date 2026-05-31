from flask import Blueprint, jsonify

from database import obtener_conexion
from http_codes_and_messages import HTTP_OK

salud_bp = Blueprint("salud", __name__)


# pre: ninguna.
# post: verifica que el backend y la base de datos estén funcionando correctamente.
def verificar_backend_db():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT 1")

        resultado = None

        for fila in cursor:
            resultado = fila

        cursor.close()
        conexion.close()

        return resultado

    except Exception:
        return None


# pre: ninguna (Acceso público).
# post: retorna un mensaje indicando si el backend está activo.
@salud_bp.route("/ping", methods=["GET"])
def ping():

    resultado = verificar_backend_db()

    if resultado is not None:
        estado_db = "Conectada"
        test_db = str(resultado)

    else:
        estado_db = "Desconectada o en error"
        test_db = "Fallo de conexión"

    respuesta = {
        "mensaje": "Backend activo y respondiendo",
        "base_de_datos": estado_db,
        "resultado_test": test_db,
    }

    return jsonify(respuesta), HTTP_OK
