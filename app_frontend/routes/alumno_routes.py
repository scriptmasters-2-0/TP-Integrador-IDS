"""Rutas del area de alumnos."""

import requests
from flask import Blueprint, redirect, render_template, session
import config
from services.api_client import obtener_perfil_usuario, obtener_prestamos, obtener_detalle_prestamo

alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")

@alumno_bp.route("/perfil")
def perfil():
    """Renderiza la página de perfil del alumno, inyectando datos del backend.

    Returns:
        str: Plantilla HTML renderizada con los datos del usuario.
    """
    try:
        usuario = obtener_perfil_usuario()
    except Exception as e:
        # Mock Fallback
        usuario = {
            "nombre": "Juan Pérez (Mock)",
            "email": "jperez@fi.uba.ar",
            "legajo": "102345",
            "rol": "alumno",
            "carrera": "Ingeniería Informática"
        }

    return render_template("alumno/perfil.html", usuario=usuario)


@alumno_bp.route("/historial")
def historial():
    """Renderiza el historial de préstamos del alumno, inyectando datos del backend.

    Returns:
        str: Plantilla HTML renderizada con el listado de préstamos.
    """
    try:
        datos_api = obtener_prestamos()
        
        historial_datos = []
        for prestamo in datos_api:
            historial_datos.append({
                "fecha": prestamo.get("fecha_retiro", "Desconocida"),
                "nombre_equipo": f"Artículo ID: {prestamo.get('id_reservado')}",
                "id_equipo": prestamo.get("id_reservado"),
                "sede": "Sede FIUBA",
                "estado_texto": prestamo.get("estado_reserva", "Pendiente"),
                "estado_clase": "badge-warning" if prestamo.get("estado_reserva") == "pendiente" else "badge-success"
            })
    except Exception:
        # Mock Fallback
        historial_datos = [
            {
                "fecha": "15 May 2026",
                "nombre_equipo": "Osciloscopio Digital Tektronix (Mock)",
                "id_equipo": "OSC-004",
                "sede": "Paseo Colón",
                "estado_texto": "Devuelto a tiempo",
                "estado_clase": "badge-success"
            },
            {
                "fecha": "02 May 2026",
                "nombre_equipo": "Libro: Física Universitaria Vol. 2 (Mock)",
                "id_equipo": "LIB-99",
                "sede": "Las Heras",
                "estado_texto": "Devuelto con demora",
                "estado_clase": "badge-warning"
            }
        ]

    return render_template("alumno/historial.html", historial=historial_datos)


@alumno_bp.route("/prestamos/<int:id>/comprobante")
def comprobante(id):
    """Renderiza el comprobante de un préstamo específico para el alumno.

    Args:
        id (int): El ID único del préstamo.

    Returns:
        str: Plantilla HTML renderizada con los datos del comprobante.
    """
    try:
        datos_api = obtener_detalle_prestamo(id)
        prestamo = {
            "id": datos_api.get("id", id),
            "estado_texto": datos_api.get("estado_reserva", "Pendiente"),
            "estado_clase": "status-active",
            "equipo_nombre": datos_api.get("nombre_art", "Material no especificado"),
            "equipo_id": datos_api.get("id_reservado", "N/A"),
            "sede": datos_api.get("seccion", "Sede Central FIUBA"),
            "fecha_reserva": datos_api.get("fecha_retiro", "N/A"),
            "fecha_retiro": datos_api.get("fecha_retiro", "N/A"),
            "fecha_limite": datos_api.get("fecha_regreso", "N/A"),
            "titular_nombre": datos_api.get("nombre", "Alumno"),
            "titular_legajo": datos_api.get("id_usuario", "N/A")
        }
    except Exception:
        # Mock Fallback
        prestamo = {
            "id": id,
            "estado_texto": "Aprobado (Listo para retirar)",
            "estado_clase": "status-active",
            "equipo_nombre": "Proyector Epson WXGA",
            "equipo_id": "PRJ-012",
            "sede": "Paseo Colón - Aula 204",
            "fecha_reserva": "15 May 2026 - 14:00 hs",
            "fecha_retiro": "15 May 2026 - 15:00 hs",
            "fecha_limite": "15 May 2026 - 18:00 hs",
            "titular_nombre": "Juan Pérez",
            "titular_legajo": "102345"
        }
    
    return render_template("alumno/comprobante.html", prestamo=prestamo)
