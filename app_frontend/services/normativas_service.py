import requests
from requests.exceptions import RequestException

from config import BACKEND_URL

TIMEOUT = 5


def obtener_normativas():
    try:
        resp = requests.get(f"{BACKEND_URL}/normativas/", timeout=TIMEOUT)

        resp.raise_for_status()
        return resp.json()

    except RequestException:
        return []

    except Exception:
        return []


def crear_normativa(data):
    try:
        resp = requests.post(f"{BACKEND_URL}/normativas/", json=data, timeout=TIMEOUT)

        resp.raise_for_status()
        return resp.json()

    except RequestException:
        return {}

    except Exception:
        return {}


def actualizar_normativa(id_normativa, data):
    try:
        resp = requests.put(
            f"{BACKEND_URL}/normativas/{id_normativa}", json=data, timeout=TIMEOUT
        )

        resp.raise_for_status()
        return resp.json()

    except RequestException:
        return {}

    except Exception:
        return {}


def eliminar_normativa(id_normativa):
    try:
        resp = requests.delete(
            f"{BACKEND_URL}/normativas/{id_normativa}", timeout=TIMEOUT
        )

        resp.raise_for_status()
        return True

    except RequestException:
        return False

    except Exception:
        return False
