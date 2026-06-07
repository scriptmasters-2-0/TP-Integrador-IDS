# loans_service.py
# Funciones de servicio para consumir endpoints /loans
import requests
from requests.exceptions import RequestException
from services.api_client import get_json

BASE_URL = "http://localhost:5000/api"
TIMEOUT = 5


def obtener_prestamos(params=None):
    """
    GET /loans
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    url = f"{BASE_URL}/loans"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []


def crear_prestamo(loan_data):
    """
    POST /loans
    Devuelve el JSON del préstamo creado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BASE_URL}/loans"
    try:
        resp = requests.post(url, json=loan_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_prestamo(loan_id):
    """
    GET /loans/{id}
    Devuelve el JSON del préstamo en caso de éxito, {} en caso de fallo.
    """
    url = f"{BASE_URL}/loans/{loan_id}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def establecer_estado_prestamo(loan_id, status_data):
    """
    PATCH /loans/{id}/status
    status_data: dict (ej., {"status": "returned"})
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BASE_URL}/loans/{loan_id}/status"
    try:
        resp = requests.patch(url, json=status_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}

def obtener_qr_reserva(id_reserva):
    url = f"/qr/loans/{id_reserva}"
    return get_json(url)