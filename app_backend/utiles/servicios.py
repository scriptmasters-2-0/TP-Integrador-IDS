"""Implementa funciones de servicio de base de datos."""

import logging

import mysql.connector
from mysql.connector import errorcode

from config import CONDICIONES_DEVOLUCION
from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_CONFLICT,
    HTTP_INTERNAL_SERVER_ERROR,
    MSG_DB_CONNECTION_FAILED,
    MSG_INTERNAL_SERVER_ERROR,
)

logger = logging.getLogger(__name__)


def verificar_backend_db():
    """Verifica que la conexión con la base de datos esté activa.

    Returns:
        tuple | None: Resultado de la consulta de prueba si tiene éxito,
            None si ocurre un error.

    """
    try:
        conexion = obtener_conexion()
        if conexion is None:
            return None

        cursor = conexion.cursor()

        cursor.execute("SELECT 1")

        resultado = None

        for fila in cursor:
            resultado = fila

        cursor.close()
        conexion.close()

        return resultado

    except Exception:
        return None


def revertir_transaccion(conn):
    """Intenta revertir las operaciones en la base de datos."""
    try:
        conn.rollback()
    except Exception:
        logger.exception("No se pudo revertir la transacción")


def revertir_transaccion_normativas(conn):
    """Intenta revertir las operaciones en la base de datos hechas en normativas."""
    try:
        conn.rollback()
    except Exception:
        logger.exception("No se pudo revertir la transacción de normativas")


def usuario_existe(id_usuario):
    """Verifica si un usuario existe en la base de datos.

    Args:
        id_usuario (int): Identificador del usuario a verificar.

    Returns:
        tuple: Existencia del usuario y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return False, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM usuario WHERE id = %s", (id_usuario,))
        return cursor.fetchone() is not None, None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def eliminar_usuario_db(id_usuario):
    """Elimina un usuario de la base de datos.

    Args:
        id_usuario (int): Identificador del usuario a eliminar.
            Debe ser un entero positivo.

    Returns:
        tuple: (eliminado, error, status), con error y status en None
            cuando la eliminación fue procesada sin fallos.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return False, MSG_DB_CONNECTION_FAILED, HTTP_INTERNAL_SERVER_ERROR

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM usuario WHERE id = %s", (id_usuario,))
        conexion.commit()
        return cursor.rowcount > 0, None, None
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ROW_IS_REFERENCED_2:  # FOREIGN_KEY_CONSTRAIN_ERRNO
            return (
                False,
                "No se pudo eliminar el usuario por una restricción de base de datos",
                HTTP_CONFLICT,
            )
        return False, MSG_INTERNAL_SERVER_ERROR, HTTP_INTERNAL_SERVER_ERROR
    except Exception:
        return False, MSG_INTERNAL_SERVER_ERROR, HTTP_INTERNAL_SERVER_ERROR
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if conexion:
                conexion.close()
        except Exception:
            pass


def listar_penalizaciones_db():
    """Obtiene todas las penalizaciones de la base de datos.

    Returns:
        tuple: Lista de penalizaciones y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM penalizacion")
        return cursor.fetchall(), None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def crear_penalizacion_db(id_usuario, motivo, severidad="media", id_reserva=None):
    """Inserta una nueva penalización activa en la base de datos.

    Crea una penalización con duración de 15 días a partir de la
    fecha actual.

    Args:
        id_usuario (int): Identificador del usuario a penalizar.
            Debe ser un entero positivo.
        motivo (str): Motivo de la penalización. No debe estar vacío.
        severidad (str): Severidad de la penalización ('baja', 'media', 'alta').
            Por defecto 'media'.
        id_reserva (int): Identificador opcional de la reserva asociada.

    Returns:
        tuple: Identificador generado y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO penalizacion (id_usuario, id_reserva, motivo, fecha_inicio, fecha_fin, activa, severidad)
            VALUES (%s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 15 DAY), TRUE, %s)
            """,
            (id_usuario, id_reserva, motivo, severidad),
        )
        conexion.commit()
        return cursor.lastrowid, None
    except mysql.connector.Error as err:
        logger.error("Error de base de datos al crear penalización: %s", err)
        return None, MSG_INTERNAL_SERVER_ERROR
    except Exception:
        logger.exception("Error inesperado al crear penalización")
        return None, MSG_INTERNAL_SERVER_ERROR
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def obtener_penalizacion_por_id(id_penalizacion):
    """Obtiene una penalización por su identificador.

    Args:
        id_penalizacion (int): Identificador de la penalización a buscar.

    Returns:
        tuple: Penalización encontrada y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM penalizacion WHERE id = %s", (id_penalizacion,))
        return cursor.fetchone(), None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def existe_reserva(id_reserva):
    """Verifica si una reserva existe en la base de datos.

    Args:
        id_reserva (int): Identificador de la reserva a verificar.

    Returns:
        tuple: Existencia de la reserva y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return False, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM reserva WHERE id = %s", (id_reserva,))
        return cursor.fetchone() is not None, None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def obtener_reserva_por_id(id_reserva):
    """Obtiene los datos de una reserva por su identificador.

    Args:
        id_reserva (int): Identificador de la reserva a buscar.

    Returns:
        tuple: Reserva encontrada y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id,
                   id_usuario,
                   id_reservado,
                   fecha_retiro,
                   fecha_regreso
            FROM reserva
            WHERE id = %s
            """,
            (id_reserva,),
        )
        return cursor.fetchone(), None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def obtener_detalle_reserva_db(reserva_id):
    """Obtiene el detalle completo de un préstamo.

    Args:
        reserva_id (int): Identificador único del préstamo a consultar.

    Returns:
        tuple: Reserva encontrada y error de conexión si corresponde.

    """
    conexion = obtener_conexion()
    if conexion is None:
        return None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                reserva.id,
                reserva.id_usuario,
                reserva.id_reservado,
                usuario.nombre,
                usuario.email,
                usuario.carrera,
                articulos.nombre_art,
                reserva.estado_reserva,
                reserva.fecha_retiro,
                reserva.fecha_regreso,
                estado_devuelto.dias_retraso,
                estado_devuelto.condiciones,
                CASE estado_devuelto.condiciones
                    WHEN 'Buen estado (sin daños)' THEN 'bueno'
                    WHEN 'Dañado (requiere revisión)' THEN 'danado'
                    WHEN 'Extraviado / no devuelto' THEN 'perdido'
                    ELSE NULL
                END AS estado_devuelto
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            LEFT JOIN estado_devuelto
                ON estado_devuelto.id_reserva = reserva.id
            WHERE reserva.id = %s
            """,
            (reserva_id,),
        )

        reserva = None

        for fila in cursor:
            reserva = fila

        return reserva, None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass


def obtener_sql_reporte(tipo_reporte):
    """Devuelve la consulta base del reporte solicitado."""
    consultas = {
        "atrasados": """
            SELECT
                usuario.nombre,
                articulos.nombre_art,
                estado_devuelto.dias_retraso,
                estado_devuelto.condiciones
            FROM estado_devuelto
            JOIN reserva
                ON estado_devuelto.id_reserva = reserva.id
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            WHERE estado_devuelto.dias_retraso > 0
        """,
        "pendientes": """
            SELECT
                reserva.id,
                usuario.nombre,
                articulos.nombre_art,
                reserva.estado_reserva
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            WHERE reserva.estado_reserva = 'pendiente'
        """,
        "devueltos": """
            SELECT
                reserva.id,
                usuario.nombre,
                articulos.nombre_art,
                reserva.estado_reserva
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            WHERE reserva.estado_reserva = 'devuelto'
        """,
        "todos": """
            SELECT
                reserva.id,
                usuario.nombre,
                articulos.nombre_art,
                reserva.estado_reserva
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
        """,
        "carreras": """
            SELECT
                usuario.carrera,
                COUNT(*) AS cantidad_reservas
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            GROUP BY usuario.carrera
            ORDER BY cantidad_reservas DESC
        """,
        "articulos": """
            SELECT
                articulos.nombre_art,
                COUNT(reserva.id) AS cantidad_reservas
            FROM reserva
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            GROUP BY articulos.nombre_art
            ORDER BY cantidad_reservas DESC
        """,
    }
    return consultas.get(tipo_reporte)


def obtener_reporte_db(tipo_reporte, limit, offset):
    """Obtiene los datos paginados del reporte solicitado desde la base de datos.

    Args:
        tipo_reporte (str): El tipo de reporte a obtener
            ('pendientes', 'devueltos', 'atrasados', 'todos', 'carreras', 'articulos').
        limit (int): Cantidad máxima de registros.
        offset (int): Posición inicial de registros.

    Returns:
        tuple: Datos, total y error de conexión si corresponde.

    """
    conn = obtener_conexion()
    if conn is None:
        return None, None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        sql_base = obtener_sql_reporte(tipo_reporte)
        cursor.execute(f"SELECT COUNT(*) AS total FROM ({sql_base}) AS reporte")
        total = cursor.fetchone()["total"]

        cursor.execute(
            f"""
            {sql_base}
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            {"limit": limit, "offset": offset},
        )
        resultado = list(cursor)

        return resultado, total, None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def sumar_stock(cursor, articulo_id):
    """Aumenta el stock de un articulo en 1."""
    cursor.execute(
        """
        UPDATE articulos
        SET stock = stock + 1
        WHERE id = %(articulo_id)s
        """,
        {"articulo_id": articulo_id},
    )


def restar_stock_si_hay(cursor, articulo_id):
    """Disminulle el stock de un articulo en 1 si es mayor a 0."""
    cursor.execute(
        """
        UPDATE articulos
        SET stock = stock - 1
        WHERE id = %(articulo_id)s
          AND stock > 0
        """,
        {"articulo_id": articulo_id},
    )
    return cursor.rowcount > 0


def registrar_devolucion(cursor, reserva, estado_devuelto):
    """Registra devolucion de una reserva."""
    condicion = CONDICIONES_DEVOLUCION.get(estado_devuelto)
    if condicion is None:
        return

    condiciones, necesita_reparacion = condicion
    cursor.execute(
        """
        DELETE FROM estado_devuelto
        WHERE id_reserva = %(id_reserva)s
        """,
        {"id_reserva": reserva.get("id")},
    )
    cursor.execute(
        """
        INSERT INTO estado_devuelto (id_reserva, dias_retraso, condiciones)
        VALUES (
            %(id_reserva)s,
            GREATEST(DATEDIFF(CURDATE(), DATE(%(fecha_regreso)s)), 0),
            %(condiciones)s
        )
        """,
        {
            "id_reserva": reserva.get("id"),
            "fecha_regreso": reserva.get("fecha_regreso"),
            "condiciones": condiciones,
        },
    )
    if necesita_reparacion:
        cursor.execute(
            """
            UPDATE articulos
            SET necesita_reparacion = 1
            WHERE id = %(articulo_id)s
            """,
            {"articulo_id": reserva.get("id_reservado")},
        )
    else:
        cursor.execute(
            """
            UPDATE articulos
            SET necesita_reparacion = 0
            WHERE id = %(articulo_id)s
            """,
            {"articulo_id": reserva.get("id_reservado")},
        )
