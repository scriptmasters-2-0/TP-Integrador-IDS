# items_service.py
# Funciones de servicio para consumir endpoints /items
import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:5001/api"
TIMEOUT = 5


def obtener_items(params=None):
    """
    GET /items
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    url = f"{BASE_URL}/items"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []


def crear_item(item_data):
    """
    POST /items
    Devuelve el JSON creado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BASE_URL}/items"
    try:
        resp = requests.post(url, json=item_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_item(item_id):
    """
    GET /items/{id}
    Devuelve el JSON del ítem en caso de éxito, {} en caso de fallo.
    """
    url = f"{BASE_URL}/items/{item_id}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def actualizar_item(item_id, item_data):
    """
    PUT /items/{id}
    Devuelve el JSON actualizado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BASE_URL}/items/{item_id}"
    try:
        resp = requests.put(url, json=item_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def eliminar_item(item_id):
    """
    DELETE /items/{id}
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BASE_URL}/items/{item_id}"
    try:
        resp = requests.delete(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}


def establecer_condicion_item(item_id, condition_data):
    """
    PATCH /items/{id}/condition
    condition_data: dict (ej., {"condition": "good"})
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BASE_URL}/items/{item_id}/condition"
    try:
        resp = requests.patch(url, json=condition_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}
