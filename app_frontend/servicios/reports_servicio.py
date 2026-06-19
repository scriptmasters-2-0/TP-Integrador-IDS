# reports_servicio.py
# Funciones de servicio para consumir endpoints/reportes
from servicios.api_client import get_json
from servicios.paginacion_servicio import extraer_data_paginada

TIMEOUT = 5


def obtener_reportes(tipo="carreras", token=None, params=None):
    """GET /reports.

    tipo: carreras

    Devuelve el JSON de los reportes de las carreras en caso de éxito, vacio en caso de falla
    """
    query_params = {"type": tipo}
    if params:
        query_params.update(params)

    payload, error = get_json("/reports", token=token, params=query_params)
    if error:
        return {}
    if not isinstance(payload, dict):
        return {}

    return {
        "tipo_reporte": payload.get("tipo_reporte", tipo),
        "formato_solicitado": payload.get("formato_solicitado"),
        "datos": extraer_data_paginada(payload),
        "pagination": payload.get("pagination") or {},
        "links": payload.get("links") or {},
    }
