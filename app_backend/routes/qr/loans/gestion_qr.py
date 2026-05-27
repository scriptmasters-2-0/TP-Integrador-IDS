import io
import base64
import json
import qrcode
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from constants import HTTP_OK, HTTP_NOT_FOUND, QR_TAMANIO, QR_BORDE
from database import obtener_conexion

blueprint_qr = Blueprint("qr", __name__)

#pre:  datos es un string no vacío con el contenido a codificar en el QR.
#post: devuelve un string en base64 que representa la imagen PNG del QR.
def generar_qr(datos):
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

#pre:  reserva es un diccionario con las claves: 'id_reserva', 'id_reservado', 'fecha_retiro', 'fecha_regreso'.
#post: devuelve un string JSON con los datos de la reserva sin información sensible.
def construir_contenido_qr(reserva):
    datos_qr = {
        "id_reserva": reserva["id_reserva"],
        "id_articulo": reserva["id_reservado"],
        "fecha_retiro": str(reserva["fecha_retiro"]),
        "fecha_regreso": str(reserva["fecha_regreso"])
    }
    return json.dumps(datos_qr)

#pre: -
#post: devuelve un diccionario con los datos de la reserva si existe, None si no se encuentra.
def obtener_reserva_por_id(id_reserva):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reserva WHERE id_reserva = %s", (id_reserva,))
    reserva = cursor.fetchone()
    cursor.close()
    conexion.close()
    return reserva

#pre:  el request incluye un JWT válido. id_reserva es un entero correspondiente a una reserva existente.
#post: devuelve 200 con 'id_reserva' y 'qrData' (imagen en base64), 404 si no existe la reserva.
@blueprint_qr.route("/api/qr/loans/<int:id_reserva>", methods=["GET"])
@jwt_required()
def obtener_qr_reserva(id_reserva):
    reserva = obtener_reserva_por_id(id_reserva)

    if reserva is None:
        return jsonify({"error": "Reserva no encontrada"}), HTTP_NOT_FOUND

    contenido_qr = construir_contenido_qr(reserva)
    imagen_qr = generar_qr(contenido_qr)

    return jsonify({
        "id_reserva": id_reserva,
        "qrData": imagen_qr
    }), HTTP_OK