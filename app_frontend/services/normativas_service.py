import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:5001/api"
TIMEOUT = 5


def obtener_normativas():
    try:
        resp = requests.get(
            f"{BASE_URL}/normativas/",
            timeout=TIMEOUT
        )

        resp.raise_for_status()
        return resp.json()

    except RequestException:
        return []

    except Exception:
        return []


def crear_normativa(data):
    try:
        resp = requests.post(
            f"{BASE_URL}/normativas/",
            json=data,
            timeout=TIMEOUT
        )

        resp.raise_for_status()
        return resp.json()

    except RequestException:
        return {}

    except Exception:
        return {}


def actualizar_normativa(id_normativa, data):
    try:
        resp = requests.put(
            f"{BASE_URL}/normativas/{id_normativa}",
            json=data,
            timeout=TIMEOUT
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
            f"{BASE_URL}/normativas/{id_normativa}",
            timeout=TIMEOUT
        )

        resp.raise_for_status()
        return True

    except RequestException:
        return False

    except Exception:
        return False