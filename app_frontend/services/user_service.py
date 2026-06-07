# user_service.py
# Funciones de servicio para consumir endpoints /users
import requests
from requests.exceptions import RequestException

from config import BACKEND_URL

TIMEOUT = 5


def obtener_usuarios(params=None):
    """GET /users
    params: diccionario opcional para parámetros de consulta
    Devuelve una lista en caso de éxito, [] en caso de fallo.
    """
    url = f"{BACKEND_URL}/users"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []


def crear_usuario(user_data):
    """POST /users
    user_data: dict
    Devuelve el JSON parseado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/users"
    try:
        resp = requests.post(url, json=user_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_usuario(user_id):
    """GET /users/{id}
    Devuelve el JSON del usuario en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/users/{user_id}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def actualizar_usuario(user_id, user_data):
    """PUT /users/{id}
    Devuelve el JSON actualizado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/users/{user_id}"
    try:
        resp = requests.put(url, json=user_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def eliminar_usuario(user_id):
    """DELETE /users/{id}
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/users/{user_id}"
    try:
        resp = requests.delete(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}


def establecer_estado_usuario(user_id, status_data):
    """PATCH /users/{id}/status
    status_data: dict (ej., {"active": True})
    Devuelve True en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/users/{user_id}/status"
    try:
        resp = requests.patch(url, json=status_data, timeout=TIMEOUT)
        resp.raise_for_status()
        return True
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_prestamos_usuario(user_id, params=None):
    """GET /users/{id}/loans
    Devuelve una lista de préstamos del usuario en caso de éxito, [] en caso de fallo.
    """
    url = f"{BACKEND_URL}/users/{user_id}/loans"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []


def obtener_penalizaciones_usuario(user_id, params=None):
    """GET /users/{id}/penalties
    Devuelve una lista de penalizaciones del usuario en caso de éxito, [] en caso de fallo.
    """
    url = f"{BACKEND_URL}/users/{user_id}/penalties"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return []
    except Exception:
        return []
