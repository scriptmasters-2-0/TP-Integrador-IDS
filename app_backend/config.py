import os
from dotenv import find_dotenv, load_dotenv

# Localiza y carga el archivo .env más cercano
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)

SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'

# Ajustes de enlace del servidor
HOST = os.environ.get('BACKEND_HOST', '127.0.0.1')
PORT = int(os.environ.get('BACKEND_PORT', '5000'))

DB_HOST = os.environ.get('DB_HOST', 'db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
DB_NAME = os.environ.get('DB_NAME', 'sistema_prestamos')
DB_PORT = int(os.environ.get('DB_PORT', 3306))