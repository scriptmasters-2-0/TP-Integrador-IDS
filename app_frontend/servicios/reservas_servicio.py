# reservas_servicio.py
# Funciones de servicio para consumir endpoints /reservas
from servicios.api_client import get_json, post_json, patch_json
from servicios.paginacion_servicio import extraer_data_paginada

BADGE_CLASSES = {
    "pendiente": "badge-warning",
    "aprobado": "badge-success",
    "entregado": "badge-success",
    "devuelto": "badge-success",
    "cancelado": "badge-danger",
    "rechazado": "badge-danger",
}

STATUS_CLASSES = {
    "pendiente": "status-pending",
    "aprobado": "status-active",
    "entregado": "status-active",
    "devuelto": "status-devuelto",
    "cancelado": "status-cancelado",
    "rechazado": "status-rechazado",
}


def badge_class(estado):
    return BADGE_CLASSES.get(estado, "badge-success")


def status_class(estado):
    return STATUS_CLASSES.get(estado, "status-active")

def obtener_reservas(params=None, token=None):
    """GET /reservas
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    payload, error = get_json("/reservas", token=token, params=params)
    if error:
        return []
    return payload or []


def crear_reserva(reserva_data, token=None):
    """POST /reservas
    Devuelve (payload, error, status) para que la ruta decida el flujo.
    """
    return post_json("/reservas", reserva_data, token=token)


def obtener_reserva(reserva_id, token=None):
    """GET /reservas/{id}
    Devuelve (payload, error) con {} como fallback.
    """
    payload, error = get_json(f"/reservas/{reserva_id}", token=token)
    return payload or {}, error


def obtener_detalle_reserva(reserva_id, token=None):
    """Obtiene una reserva o levanta excepción si el backend devuelve error."""
    payload, error = get_json(f"/reservas/{reserva_id}", token=token)
    if error:
        raise Exception(error)
    return payload


def establecer_estado_reserva(reserva_id, status_data, token=None):
    """PATCH /reservas/{id}/status
    status_data: dict (ej., {"status": "returned"})
    Devuelve (ok, error, status) para que la ruta decida el flujo.
    """
    
    payload, error, status = patch_json(f"/reservas/{reserva_id}/status", status_data, token=token)
    if error:
        return False, error, status
    return True, None, status


def obtener_qr_reserva(id_reserva, token=None):
    """Descripción: función obtener_qr_reserva."""
    return get_json(f"/qr/reservas/{id_reserva}", token=token)


def obtener_solicitudes(token=None):
    """GET /reservas/solicitudes
    Devuelve una lista de reservas pendientes
    """
    payload, error = get_json("/reservas/solicitudes", token=token)
    if error:
        return []
    return extraer_data_paginada(payload)


def escanear_qr_reserva(id_reserva, token=None):
    """PATCH /reservas/<int:id_reserva>/scan"""
    payload, error, status = patch_json(f"/reservas/{id_reserva}/scan", token=token, data={})

    if error:
        return None, error

    return payload, None
