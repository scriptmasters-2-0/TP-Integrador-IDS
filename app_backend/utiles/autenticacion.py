"""Implementa utilidades de autenticación."""

import logging
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import jsonify, request

from config import JWT_ALGORITMO, JWT_HORAS_DE_EXPIRACION, JWT_SECRETO
from http_codes_and_messages import HTTP_UNAUTHORIZED, MSG_UNAUTHORIZED

logger = logging.getLogger(__name__)


def hashear_contrasenia(contrasenia):
    """Genera el hash de una contraseña usando bcrypt.

    Args:
        contrasenia (str): Contraseña en texto plano a hashear.

    Returns:
        str: Hash de la contraseña codificado en UTF-8.

    """
    hash_bytes = bcrypt.hashpw(contrasenia.encode("utf-8"), bcrypt.gensalt())

    return hash_bytes.decode("utf-8")


def validar_contrasenia(contrasenia, contrasenia_hash):
    """Verifica si una contraseña coincide con su hash.

    Args:
        contrasenia (str): Contraseña en texto plano a verificar.
        contrasenia_hash (str): Hash almacenado contra el cual comparar.

    Returns:
        bool: True si la contraseña coincide con el hash, False en caso contrario.

    """
    try:
        return bcrypt.checkpw(contrasenia.encode("utf-8"), contrasenia_hash.encode("utf-8"))

    except (ValueError, TypeError):
        logger.warning("Error al verificar la contraseña")
        return False


def generar_token(usuario_id, rol):
    """Genera un token JWT con el ID de usuario y su rol.

    Args:
        usuario_id (int): Identificador único del usuario.
        rol (str): Rol del usuario en el sistema.

    Returns:
        str: Token JWT codificado.

    """
    payload = {
        "usuario_id": usuario_id,
        "rol": rol,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_HORAS_DE_EXPIRACION),
    }

    return jwt.encode(payload, JWT_SECRETO, algorithm=JWT_ALGORITMO)


def decodificar_token(token):
    """Decodifica y valida un token JWT.

    Args:
        token (str): Token JWT a decodificar.

    Returns:
        tuple: Una tupla (payload, mensaje) donde payload es un diccionario
            con los datos del token si es válido o None si no lo es, y
            mensaje es un string indicando el estado ("Válido", "Token expirado"
            o "Token inválido").

    """
    try:
        return jwt.decode(token, JWT_SECRETO, algorithms=[JWT_ALGORITMO]), "Válido"

    except jwt.ExpiredSignatureError:
        return None, "Token expirado"

    except jwt.InvalidTokenError:
        return None, "Token inválido"


def extraer_token_del_header():
    """Extrae el token JWT del header Authorization de la petición.

    Espera un header con formato "Bearer <token>".

    Returns:
        tuple: Una tupla (token, mensaje) donde token es el string del JWT
            si se extrajo correctamente o None si el formato es incorrecto,
            y mensaje indica el estado ("OK" o "Tipo de token incorrecto").

    """
    header = request.headers.get("Authorization", "")

    if not header.startswith("Bearer "):
        return None, "Tipo de token incorrecto"

    return header[len("Bearer ") :].strip(), "OK"


# decorator
def requiere_auth(roles):
    """Decorador que protege una ruta requiriendo autenticación y un rol específico.

    Verifica que la petición incluya un token JWT válido en el header
    Authorization y que el rol del usuario coincida con el rol requerido.

    Args:
        roles (str): Roles requeridos para acceder a la ruta protegida.

    Returns:
        function: Decorador que envuelve la función de ruta con la
            validación de autenticación y autorización.

    """

    def wrapperGenerator(route):

        @wraps(route)
        def wrapper(*args, **kwargs):
            """Descripción: función wrapper."""
            token, tokenError = extraer_token_del_header()

            if token is None:
                return jsonify({"error": tokenError}), HTTP_UNAUTHORIZED

            payload, payloadError = decodificar_token(token)

            if payload is None:
                return jsonify({"error": payloadError}), HTTP_UNAUTHORIZED

            if payload.get("rol") not in roles:
                return jsonify({"error": MSG_UNAUTHORIZED}), HTTP_UNAUTHORIZED

            request.usuario_id = payload.get("usuario_id")
            request.usuario_rol = payload.get("rol")

            return route(*args, **kwargs)

        return wrapper

    return wrapperGenerator

