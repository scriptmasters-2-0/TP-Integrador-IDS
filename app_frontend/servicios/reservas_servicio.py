# reservas_servicio.py
# Funciones de servicio para consumir endpoints /reservas
from flask import session

from servicios.api_client import get_json, post_json, patch_json

TIMEOUT = 5


def obtener_reservas(params=None):
    """GET /reservas
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json("/reservas", params=params)
    if error:
        return []
    return payload or []


def crear_reserva(reserva_data):
    """POST /reservas
    Devuelve el JSON del préstamo creado en caso de éxito, {} en caso de fallo.
    """
    payload, error, status = post_json("/reservas", reserva_data)
    if error:
        return {}
    return payload or {}


def obtener_reserva(reserva_id):
    """GET /reservas/{id}
    Devuelve el JSON del préstamo en caso de éxito, {} en caso de fallo.
    """
    payload, error = get_json(f"/reservas/{reserva_id}")
    if error:
        return {}
    return payload or {}


def establecer_estado_reserva(reserva_id, status_data):
    """PATCH /reservas/{id}/status
    status_data: dict (ej., {"status": "returned"})
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    print("data:", status_data)
    payload, error, status = patch_json(f"/reservas/{reserva_id}/status", status_data)
    if error:
        return False
    return True


def obtener_qr_reserva(id_reserva):
    """Descripción: función obtener_qr_reserva."""
    return get_json(f"/qr/reservas/{id_reserva}")


def obtener_solicitudes():
    """GET /reservas/solicitudes
    Devuelve una lista de reservas pendientes
    """
    payload, error = get_json("/reservas/solicitudes")

    if error:
        return []
    
    return payload or []
