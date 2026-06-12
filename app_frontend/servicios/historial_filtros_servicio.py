"""Filtros reutilizables para historiales de reservas."""

from datetime import date, datetime
import unicodedata

MSG_FECHAS_INVALIDAS = "Ingresá fechas válidas."
MSG_RANGO_INVALIDO = "La fecha desde no puede ser posterior a la fecha hasta."


def normalizar_texto(valor):
    """Normaliza texto para comparar sin mayusculas ni tildes."""
    texto = str(valor or "").casefold()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")


def _parsear_fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if not valor:
        return None

    texto = str(valor).strip()
    if not texto:
        return None

    try:
        return date.fromisoformat(texto[:10])
    except ValueError:
        return None


def _parsear_fecha_filtro(valor):
    if not valor:
        return None, None

    texto = str(valor).strip()
    if not texto:
        return None, None

    try:
        return date.fromisoformat(texto), None
    except ValueError:
        return None, MSG_FECHAS_INVALIDAS


def validar_fechas_filtros(filtros):
    """Valida fechas de filtros y devuelve fechas parseadas junto al error."""
    filtros = filtros or {}
    fecha_desde, error_desde = _parsear_fecha_filtro(filtros.get("fecha_desde"))
    fecha_hasta, error_hasta = _parsear_fecha_filtro(filtros.get("fecha_hasta"))

    if error_desde or error_hasta:
        return None, None, MSG_FECHAS_INVALIDAS
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        return None, None, MSG_RANGO_INVALIDO

    return fecha_desde, fecha_hasta, None


def _coincide_texto(reserva, busqueda):
    if not busqueda:
        return True

    if busqueda.isdecimal():
        ids = (
            str(reserva.get("id") or ""),
            str(reserva.get("id_equipo") or ""),
        )
        return busqueda in ids

    return busqueda in normalizar_texto(reserva.get("nombre_equipo"))


def _coincide_estado(reserva, estado):
    if not estado:
        return True
    return str(reserva.get("estado_texto") or "") == estado


def _coincide_fechas(reserva, fecha_desde, fecha_hasta):
    fecha_reserva = _parsear_fecha(reserva.get("fecha_filtro"))
    if fecha_reserva is None:
        return not fecha_desde and not fecha_hasta
    if fecha_desde and fecha_reserva < fecha_desde:
        return False
    if fecha_hasta and fecha_reserva > fecha_hasta:
        return False
    return True


def filtrar_historial_reservas(reservas, filtros):
    """Aplica filtros acumulativos de texto, estado y fechas."""
    filtros = filtros or {}
    busqueda = normalizar_texto(filtros.get("q"))
    estado = str(filtros.get("estado") or "").strip()
    fecha_desde, fecha_hasta, filter_error = validar_fechas_filtros(filtros)

    resultado = [
        reserva
        for reserva in reservas or []
        if _coincide_texto(reserva, busqueda)
        and _coincide_estado(reserva, estado)
        and (filter_error is not None or _coincide_fechas(reserva, fecha_desde, fecha_hasta))
    ]
    return resultado, filter_error


def estados_disponibles(reservas):
    """Devuelve los estados presentes en el historial, ordenados para el select."""
    estados = {
        str(reserva.get("estado_texto") or "").strip()
        for reserva in reservas or []
        if str(reserva.get("estado_texto") or "").strip()
    }
    return sorted(estados)
