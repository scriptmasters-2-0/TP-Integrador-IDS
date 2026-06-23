"""Configuración del servidor backend.

Carga las variables de entorno desde un archivo .env y define
las constantes de configuración para el servidor, la base de datos,
JWT y generación de códigos QR.
"""

import logging
import os

from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)

# Localiza y carga el archivo .env más cercano
env_path = find_dotenv()
if env_path:
    if not load_dotenv(env_path):
        logger.warning(
            "No se pudo cargar el archivo .env, usando valores por defecto: %s",
            env_path,
        )

DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

# Ajustes de enlace del servidor
HOST = os.environ.get("BACKEND_HOST", "127.0.0.1")
PORT = int(os.environ.get("BACKEND_PORT", "5000"))

# Base de datos
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_NAME = os.environ.get("DB_NAME", "sistema_prestamos")
DB_ROOT_PASSWORD = os.environ.get("DB_ROOT_PASSWORD", "contrasenia")
DB_USER = os.environ.get("DB_USER", "tp_integrador")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "contrasenia")

# JWT settings
JWT_SECRETO = os.environ.get("JWT_SECRETO", "secret")
JWT_HORAS_DE_EXPIRACION = int(os.environ.get("JWT_HORAS_DE_EXPIRACION", "8"))
JWT_ALGORITMO = os.environ.get("JWT_ALGORITMO", "HS256")

# QR settings
QR_BORDE = int(os.environ.get("QR_BORDER", "4"))
QR_TAMANIO = int(os.environ.get("QR_TAMANIO", "10"))
