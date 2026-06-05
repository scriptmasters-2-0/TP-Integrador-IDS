import requests
from flask import session
import config

def get_auth_headers():
    """Genera los headers de autenticación si existe un token en sesión.

    Returns:
        dict: Diccionario con el header de Authorization, o vacío si no hay token.
    """
    token = session.get("jwt_token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def obtener_perfil_usuario():
    """Llama a la API para obtener el perfil del usuario autenticado.

    Returns:
        dict: Datos del perfil del usuario obtenidos de la base de datos.

    Raises:
        Exception: Si el backend no responde con éxito (HTTP 200).
    """
    response = requests.get(f"{config.BACKEND_URL}/auth/me", headers=get_auth_headers(), timeout=3)
    if response.status_code == 200:
        return response.json().get("user", response.json())
    raise Exception("No autorizado o error del backend")

def obtener_prestamos():
    """Llama a la API para obtener el listado completo de préstamos y reservas.

    Returns:
        list: Lista de diccionarios con los detalles crudos de los préstamos de MySQL.

    Raises:
        Exception: Si la obtención falla o el backend no está disponible.
    """
    response = requests.get(f"{config.BACKEND_URL}/loans", headers=get_auth_headers(), timeout=3)
    if response.status_code == 200:
        return response.json()
    raise Exception("Error al obtener prestamos")

def obtener_detalle_prestamo(loan_id):
    """Llama a la API para obtener el detalle de un préstamo específico.

    Args:
        loan_id (int): El identificador único del préstamo.

    Returns:
        dict: Detalle del préstamo con llaves provenientes del backend.

    Raises:
        Exception: Si no se encuentra el préstamo o falla la API.
    """
    response = requests.get(f"{config.BACKEND_URL}/loans/{loan_id}", headers=get_auth_headers(), timeout=3)
    if response.status_code == 200:
        return response.json()
    raise Exception("Préstamo no encontrado")
