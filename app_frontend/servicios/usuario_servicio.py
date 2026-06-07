# usuario_servicio.py
# Funciones de servicio para consumir endpoints /usuarios
import requests
from requests.exceptions import RequestException

from config import BACKEND_URL

TIMEOUT = 5


def obtener_usuarios(params=None):
    """GET /usuarios
    params: diccionario opcional para parámetros de consulta
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    url = f"{BACKEND_URL}/usuarios"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []


def crear_usuario(usuario_data):
    """POST /usuarios
    usuario_data: dict
    Devuelve el JSON parseado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/usuarios"
    try:
        resp = requests.post(url, json=usuario_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_usuario(usuario_id):
    """GET /usuarios/{id}
    Devuelve el JSON del usuario en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/usuarios/{usuario_id}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def actualizar_usuario(usuario_id, usuario_data):
    """PUT /usuarios/{id}
    Devuelve el JSON actualizado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/usuarios/{usuario_id}"
    try:
        resp = requests.put(url, json=usuario_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def eliminar_usuario(usuario_id):
    """DELETE /usuarios/{id}
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/usuarios/{usuario_id}"
    try:
        resp = requests.delete(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}


def establecer_estado_usuario(usuario_id, status_data):
    """PATCH /usuarios/{id}/status
    status_data: dict (ej., {"active": True})
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/usuarios/{usuario_id}/status"
    try:
        resp = requests.patch(url, json=status_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_reservas_usuario(usuario_id, params=None):
    """GET /usuarios/{id}/reservas
    Devuelve una lista de préstamos del usuario en caso de éxito, [] en caso de fallo.
    """
    url = f"{BACKEND_URL}/usuarios/{usuario_id}/reservas"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []


def obtener_penalizaciones_usuario(usuario_id, params=None):
    """GET /usuarios/{id}/penalizaciones
    Devuelve una lista de penalizaciones del usuario en caso de éxito, [] en caso de fallo.
    """
    url = f"{BACKEND_URL}/usuarios/{usuario_id}/penalizaciones"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []
