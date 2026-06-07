# auth_servicio.py
# Funciones de servicio para consumir endpoints /auth
import requests
from requests.exceptions import RequestException

from config import BACKEND_URL

TIMEOUT = 5


def crear_usuario(credentials):
    """POST /auth/logup
    credentials: dict (ej., {"usuarioname": "...", "email": "...", "carrera": "...", "contrasenia": "..."})
    Devuelve el JSON parseado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/auth/logup"
    try:
        resp = requests.post(url, json=credentials, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def iniciar_sesion(credentials):
    """POST /auth/login
    credentials: dict (ej., {"usuarioname": "...", "contrasenia": "..."})
    Devuelve el JSON parseado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/auth/login"
    try:
        resp = requests.post(url, json=credentials, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}


def cerrar_sesion():
    """POST /auth/logout
    Devuelve el JSON parseado en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/auth/logout"
    try:
        resp = requests.post(url, timeout=TIMEOUT)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {}
    except RequestException:
        return {}
    except Exception:
        return {}


def obtener_mi_perfil():
    """GET /auth/me
    Devuelve el JSON con la información del usuario en caso de éxito, {} en caso de fallo.
    """
    url = f"{BACKEND_URL}/auth/me"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return {}
    except Exception:
        return {}
