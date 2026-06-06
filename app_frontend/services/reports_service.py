#reports_service.py
#Funciones de servicio para consumir endpoints/reportes

import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:5001/api"
TIMEOUT = 5

def obtener_reportes(tipo="careers"):
    """
    GET /reports

    tipo: careers

    Devuelve el JSON de los reportes de las carreras en caso de éxito, vacio en caso de falla
    """

    url = f"{BASE_URL}/reports"

    try:
        response = requests.get(url, params={"type": tipo}, timeout=TIMEOUT)

        response.raise_for_status() 

        return response.json()

    except RequestException:
        return {}

    except Exception:
        return {}