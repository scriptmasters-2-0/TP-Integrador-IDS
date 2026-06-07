# penalizaciones_servicio.py
# Funciones de servicio para consumir endpoints /penalizaciones
import requests
from requests.exceptions import RequestException

from config import BACKEND_URL

TIMEOUT = 5


def obtener_penalizaciones(params=None):
    """GET /penalizaciones
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    url = f"{BACKEND_URL}/penalizaciones"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []


def crear_penalizacion(penalty_data):
    """POST /penalizaciones
    Devuelve el JSON de la penalización creada en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/penalizaciones"
    try:
        resp = requests.post(url, json=penalty_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_penalizacion(penalty_id):
    """GET /penalizaciones/{id}
    Devuelve el JSON de la penalización en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/penalizaciones/{penalty_id}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def actualizar_penalizacion(penalty_id, penalty_data):
    """PUT /penalizaciones/{id}
    Devuelve el JSON actualizado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/penalizaciones/{penalty_id}"
    try:
        resp = requests.put(url, json=penalty_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def actualizar_parcial_penalizacion(penalty_id, patch_data):
    """PATCH /penalizaciones/{id}
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/penalizaciones/{penalty_id}"
    try:
        resp = requests.patch(url, json=patch_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}
