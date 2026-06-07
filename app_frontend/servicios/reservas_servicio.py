# reservas_servicio.py
# Funciones de servicio para consumir endpoints /reservas
import requests
from flask import session
from requests.exceptions import RequestException

from config import BACKEND_URL
from servicios.api_client import get_json

TIMEOUT = 5


def obtener_reservas(params=None):
    """GET /reservas
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    url = f"{BACKEND_URL}/reservas"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []


def crear_reserva(reserva_data):
    """POST /reservas
    Devuelve el JSON del préstamo creado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/reservas"
    try:
        resp = requests.post(
            url,
            headers={"authorization": f"Bearer {session.get('token', '')}"},
            json=reserva_data,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_reserva(reserva_id):
    """GET /reservas/{id}
    Devuelve el JSON del préstamo en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/reservas/{reserva_id}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def establecer_estado_reserva(reserva_id, status_data):
    """PATCH /reservas/{id}/status
    status_data: dict (ej., {"status": "returned"})
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/reservas/{reserva_id}/status"
    try:
        resp = requests.patch(url, json=status_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_qr_reserva(id_reserva):
    url = f"/qr/reservas/{id_reserva}"
    return get_json(url)
