"""Rutas para verificar el estado del sistema.

Define el endpoint de salud (ping) para verificar la conectividad
entre el backend y la base de datos.
"""

from flask import Blueprint, jsonify

from database import obtener_conexion
from http_codes_and_messages import HTTP_OK

salud_bp = Blueprint("salud", __name__)


def verificar_backend_db():
    """Verifica que la conexión con la base de datos esté activa.

    Returns:
        tuple | None: Resultado de la consulta de prueba si tiene éxito,
            None si ocurre un error.

    """
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


@salud_bp.route("/ping", methods=["GET"])
def ping():
    """Verifica que el backend y la base de datos estén funcionando.

    Returns:
        tuple: JSON con el estado de los servicios y el código HTTP correspondiente.

    """
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
