"""Configuración del servidor backend.

Carga las variables de entorno desde un archivo .env y define
las constantes de configuración para el servidor, la base de datos,
JWT y generación de códigos QR.
"""

import os

from dotenv import find_dotenv, load_dotenv

# Localiza y carga el archivo .env más cercano
env_path = find_dotenv()
if env_path:
    if not load_dotenv(env_path):
        print("No env variables loaded, using defaults", env_path)

DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

# Ajustes de enlace del servidor
HOST = os.environ.get("BACKEND_HOST", "127.0.0.1")
PORT = int(os.environ.get("BACKEND_PORT", "5001"))

# Base de datos
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_NAME = os.environ.get("DB_NAME", "sistema_prestamos")
DB_ROOT_PASSWORD = os.environ.get("DB_ROOT_PASSWORD", "password")
DB_USER = os.environ.get("DB_USER", "tp_integrador")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")

# JWT settings
JWT_SECRET = os.environ.get("JWT_SECRET", "secret")
JWT_EXPIRATION_HORAS = int(os.environ.get("JWT_EXPIRATION_HORAS", "8"))
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

# QR settings
QR_BORDE = int(os.environ.get("QR_BORDER", "4"))
QR_TAMANIO = int(os.environ.get("QR_TAMANIO", "10"))
