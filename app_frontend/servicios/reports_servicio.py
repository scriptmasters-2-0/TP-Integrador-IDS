# reports_servicio.py
# Funciones de servicio para consumir endpoints/reportes
from servicios.api_client import get_json

TIMEOUT = 5


def obtener_reportes(tipo="careers", token=None):
    """GET /reports.

    tipo: careers

    Devuelve el JSON de los reportes de las carreras en caso de éxito, vacio en caso de falla
    """
    payload, error = get_json("/reports", token=token, params={"type": tipo})
    if error:
        return {}
    return payload or {}
