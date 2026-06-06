# loans_service.py
# Funciones de servicio para consumir endpoints /loans
import requests
from requests.exceptions import RequestException
from api_client import get_json

BASE_URL = "http://localhost:5000/api"
TIMEOUT = 5

def obtener_qr_reserva(id_reserva, token=None, params=None):
    """
    GET /qr/loans/id_reserva
    Devuelve el qr correspondiente a una reserva
    """

    url = f"{BASE_URL}/qr/loans/<int:id_reserva>"
    return get_json(url, token=token, params=params)
