"""Rutas de la API para la generación de códigos QR de reservas.

Define los endpoints para generar y obtener códigos QR asociados
a las reservas del sistema.
"""

import base64
import io
import json

import qrcode
from flask import Blueprint, jsonify

from config import QR_BORDE, QR_TAMANIO
from database import obtener_conexion
from http_codes_and_messages import HTTP_NOT_FOUND, HTTP_OK

qr_bp = Blueprint("qr", __name__)


def generar_qr(datos):
    """Genera una imagen QR codificada en base64 a partir de un string.

    Args:
        datos (str): Contenido a codificar en el código QR.
            No debe estar vacío.

    Returns:
        str: String en base64 que representa la imagen PNG del código QR.

    """
    codigo_qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=QR_TAMANIO,
        border=QR_BORDE,
    )
    codigo_qr.add_data(datos)
    codigo_qr.make(fit=True)

    imagen = codigo_qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def construir_contenido_qr(reserva):
    """Construye el contenido JSON para codificar en el código QR.

    Extrae los datos relevantes de la reserva sin incluir información
    sensible del usuario.

    Args:
        reserva (dict): Diccionario con las claves 'id_reserva',
            'id_reservado', 'fecha_retiro' y 'fecha_regreso'.

    Returns:
        str: String JSON con los datos de la reserva.

    """
    datos_qr = {
        "id_reserva": reserva["id"],
        "id_articulo": reserva["id_reservado"],
        "fecha_retiro": str(reserva["fecha_retiro"]),
        "fecha_regreso": str(reserva["fecha_regreso"]),
    }
    return json.dumps(datos_qr)


def obtener_reserva_por_id(id_reserva):
    """Obtiene los datos de una reserva por su identificador.

    Args:
        id_reserva (int): Identificador de la reserva a buscar.

    Returns:
        dict | None: Diccionario con los datos de la reserva si existe,
            None si no se encuentra.

    """
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id AS id_reserva,
               id_reservado,
               fecha_retiro,
               fecha_regreso
        FROM reserva
        WHERE id = %s
        """,
        (id_reserva,),
    )
    reserva = cursor.fetchone()
    cursor.close()
    conexion.close()
    return reserva


@qr_bp.route("/api/qr/loans/<int:id_reserva>", methods=["GET"])
def obtener_qr_reserva(id_reserva):
    """Genera y devuelve el código QR de una reserva.

    Requiere un JWT válido en el request. Busca la reserva por su
    identificador, construye el contenido del QR y genera la imagen.

    Args:
        id_reserva (int): Identificador de la reserva para la cual
            generar el código QR.

    Returns:
        tuple: Respuesta JSON con 'id_reserva' y 'qrData' (imagen en
            base64) y código HTTP 200. Retorna 404 si la reserva no existe.

    """
    reserva = obtener_reserva_por_id(id_reserva)

    if reserva is None:
        return jsonify({"error": "Reserva no encontrada"}), HTTP_NOT_FOUND

    contenido_qr = construir_contenido_qr(reserva)
    imagen_qr = generar_qr(contenido_qr)

    return jsonify({"id_reserva": id_reserva, "qrData": imagen_qr}), HTTP_OK
