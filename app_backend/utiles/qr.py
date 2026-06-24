"""Implementa utilidades del qr."""
import base64
import io
import json

import qrcode

from config import QR_BORDE, QR_TAMANIO


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

