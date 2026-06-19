"""Módulo de conexión y gestión de la base de datos.

Provee funciones para obtener conexiones a la base de datos MySQL
y para ejecutar el script de inicialización del esquema.
"""

import logging
import os

import mysql.connector

import config

logger = logging.getLogger(__name__)


def obtener_conexion():
    """Establece y retorna una conexión a la base de datos MySQL.

    Utiliza los parámetros de configuración definidos en el módulo
    config para conectarse a la base de datos.

    Returns:
        mysql.connector.connection.MySQLConnection: Conexión activa a la base
            de datos, o None si ocurre un error.

    """
    try:
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            port=config.DB_PORT,
        )
        return connection

    except mysql.connector.Error as err:
        logger.error("Error al conectar a la base de datos: %s", err)
        return None


def init_database():
    """Inicializa el esquema de la base de datos ejecutando el script SQL.

    Lee y ejecuta el archivo SQL de inicialización ubicado en
    el directorio db_scripts. Si el archivo no existe o la conexión
    falla, la función retorna sin realizar cambios.

    Raises:
        mysql.connector.Error: Si ocurre un error durante la ejecución
            del script SQL.

    """
    sql_file = os.path.join(os.path.dirname(__file__), "db_scripts", "init_db.sql")
    if not os.path.exists(sql_file):
        logger.warning("Archivo SQL de inicialización no encontrado: %s", sql_file)
        return

    conn = obtener_conexion()
    cursor = None

    if conn is None:
        return

    try:
        cursor = conn.cursor()

        with open(sql_file, "r", encoding="utf-8") as f:
            script = f.read()

        # Ejecutar múltiples sentencias separadas por ';' de forma segura
        statements = [s.strip() for s in script.split(";") if s.strip()]
        for stmt in statements:
            cursor.execute(stmt)
        conn.commit()

        logger.info("Script de inicialización de base de datos ejecutado correctamente")

    except mysql.connector.Error as err:
        logger.error("Error inicializando la base de datos: %s", err)

    except Exception as err:
        logger.exception("Error inesperado inicializando la base de datos: %s", err)

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass
