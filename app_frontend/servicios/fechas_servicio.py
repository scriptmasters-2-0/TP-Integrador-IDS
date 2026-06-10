"""Utilidades para formateo de fechas del frontend."""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

ARGENTINA_TZ = ZoneInfo("America/Argentina/Buenos_Aires")


def formatear_fecha_argentina(fecha):
    """Convierte una fecha ISO/HTTP a hora argentina para mostrar en pantalla."""
    if not fecha:
        return "Desconocida"

    try:
        if isinstance(fecha, datetime):
            fecha_dt = fecha
        else:
            fecha_texto = str(fecha)
            try:
                fecha_dt = datetime.fromisoformat(fecha_texto.replace("Z", "+00:00"))
            except ValueError:
                fecha_dt = parsedate_to_datetime(fecha_texto)

        if fecha_dt.tzinfo is None:
            fecha_dt = fecha_dt.replace(tzinfo=timezone.utc)

        fecha_argentina = fecha_dt.astimezone(ARGENTINA_TZ)
        return fecha_argentina.strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError, OverflowError):
        return str(fecha)
