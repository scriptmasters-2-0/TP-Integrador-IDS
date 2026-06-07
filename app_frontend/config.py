"""Configuración de la aplicación frontend.

Carga las variables de entorno desde un archivo .env y expone
los valores de configuración necesarios para la ejecución de la
aplicación Flask del frontend.
"""

import os

from dotenv import find_dotenv, load_dotenv

# Localiza y carga el archivo .env más cercano
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)

# Expone valores de configuración comunes con valores por defecto razonables
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
HOST = os.environ.get("FRONTEND_HOST", "127.0.0.1")
PORT = int(os.environ.get("FRONTEND_PORT", "5000"))

BACKEND_HOST = os.environ.get("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = os.environ.get("BACKEND_PORT", "5001")
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api"
