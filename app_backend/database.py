import os

import mysql.connector

import config


def obtener_conexion():
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
        print(f"Error al conectar a la base de datos: {err}")
        return None


def init_database():
    sql_file = os.path.join(os.path.dirname(__file__), "db_scripts", "init_db.sql")
    if not os.path.exists(sql_file):
        print(f"SQL initialization file not found: {sql_file}")
        return

    conn = obtener_conexion()
    cursor = None

    if conn is None:
        return

    try:
        cursor = conn.cursor()

        with open(sql_file, "r", encoding="utf-8") as f:
            script = f.read()

        cursor.execute(script)

        print("Database initialization script executed successfully.")

    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")

    except Exception as err:
        print(f"Unexpected error while initializing database: {err}")

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
