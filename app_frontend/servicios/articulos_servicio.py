# articulos_servicio.py
# Funciones de servicio para consumir endpoints /articulos
import requests
from requests.exceptions import RequestException

from config import BACKEND_URL

TIMEOUT = 5


def obtener_articulos(params=None):
    """GET /articulos
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    url = f"{BACKEND_URL}/articulos"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []


def crear_articulo(articulo_data):
    """POST /articulos
    Devuelve el JSON creado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/articulos"
    try:
        resp = requests.post(url, json=articulo_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_articulo(articulo_id):
    """GET /articulos/{id}
    Devuelve el JSON del ítem en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/articulos/{articulo_id}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def actualizar_articulo(articulo_id, articulo_data):
    """PUT /articulos/{id}
    Devuelve el JSON actualizado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/articulos/{articulo_id}"
    try:
        resp = requests.put(url, json=articulo_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def eliminar_articulo(articulo_id):
    """DELETE /articulos/{id}
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/articulos/{articulo_id}"
    try:
        resp = requests.delete(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}


def establecer_condicion_articulo(articulo_id, condition_data):
    """PATCH /articulos/{id}/condition
    condition_data: dict (ej., {"condition": "good"})
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/articulos/{articulo_id}/condition"
    try:
        resp = requests.patch(url, json=condition_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}
