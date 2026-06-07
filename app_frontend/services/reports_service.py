#reports_service.py
#Funciones de servicio para consumir endpoints/reportes

import requests
from requests.exceptions import RequestException

from config import BACKEND_URL

TIMEOUT = 5

def obtener_reportes(tipo="careers"):
    """
    GET /reports

    tipo: careers

    Devuelve el JSON de los reportes de las carreras en caso de éxito, vacio en caso de falla
    """

    url = f"{BACKEND_URL}/reports"

    try:
        response = requests.get(url, params={"type": tipo}, timeout=TIMEOUT)

        response.raise_for_status() 

        return response.json()

    except RequestException:
        return {}

    except Exception:
        return {}
