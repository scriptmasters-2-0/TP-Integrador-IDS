import mysql.connector
import config

def obtener_conexion():
    try:
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            port=config.DB_PORT
        )
        return connection
    
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None