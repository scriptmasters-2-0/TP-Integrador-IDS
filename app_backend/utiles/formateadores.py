"""Implementa formateadores."""


from config import ARGENTINA_TZ


def datetime_to_argentina_iso(value):
    """Convierte un datetime de base de datos a ISO 8601 en hora argentina."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=ARGENTINA_TZ)
    return value.astimezone(ARGENTINA_TZ).isoformat(timespec="seconds")


def formatear_articulo(row):
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
        "activo": bool(row.get("activo")),
    }


def formatear_penalizaciones(row):
    """Formatea una fila de penalización de la BD como respuesta de la API.

    Args:
        row (dict): Diccionario con los datos de la penalización obtenidos
            de la base de datos.

    Returns:
        dict: Diccionario con los campos formateados para la respuesta
            de la API.

    """
    return {
        "id": row.get("id"),
        "usuarioId": row.get("id_usuario"),
        "reservaId": row.get("id_reserva"),
        "reason": row.get("motivo"),
        "status": "Activa" if row.get("activa") else "Levantada",
        "severidad": row.get("severidad"),
        "createdAt": (row.get("fecha_inicio").isoformat() if row.get("fecha_inicio") else None),
        "resolvedAt": (row.get("fecha_fin").isoformat() if row.get("fecha_fin") else None),
    }


def formatear_reservas(row):
    """Formatea una fila de préstamo de la base de datos como respuesta de la API.

    Convierte los campos de fecha a formato ISO 8601 cuando están presentes.

    Args:
        row (dict): Diccionario con los datos del préstamo obtenidos de la
            base de datos.

    Returns:
        dict: Diccionario formateado con los campos del préstamo para la respuesta.

    """
    return {
        "id": row.get("id"),
        "id_usuario": row.get("id_usuario"),
        "usuario_nombre": row.get("usuario_nombre"),
        "id_reservado": row.get("id_reservado"),
        "nombre_art": row.get("nombre_art"),
        "estado_reserva": row.get("estado_reserva"),
        "fecha_retiro": (row.get("fecha_retiro").isoformat() if row.get("fecha_retiro") else None),
        "fecha_regreso": (row.get("fecha_regreso").isoformat() if row.get("fecha_regreso") else None),
    }


def formatear_usuario_reserva(row):
    """Formatea una reserva de usuario para evitar serialización GMT de Flask."""
    nombre_articulo = row.get("nombre_articulo")
    return {
        "id": row.get("id"),
        "id_reservado": row.get("id_reservado"),
        "nombre_articulo": nombre_articulo,
        "nombre_art": nombre_articulo,
        "estado_reserva": row.get("estado_reserva"),
        "fecha_retiro": datetime_to_argentina_iso(row.get("fecha_retiro")),
        "fecha_regreso": datetime_to_argentina_iso(row.get("fecha_regreso")),
    }

