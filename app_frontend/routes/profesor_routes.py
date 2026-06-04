"""Rutas del area de profesores."""

import requests
from flask import Blueprint, redirect, render_template, session, request
import config
from services.api_client import obtener_prestamos

profesor_bp = Blueprint("profesor", __name__, url_prefix="/profesor")

@profesor_bp.route("/dashboard")
def dashboard():
    """Renderiza el panel de control del profesor con datos del backend.

    Returns:
        str: Plantilla HTML renderizada con las reservas y estadísticas.
    """
    try:
        datos_api = obtener_prestamos()
        reservas_api = []
        for item in datos_api:
            reservas_api.append({
                "id": item.get("id"),
                "estado_clase": "status-active" if item.get("estado_reserva") != "pendiente" else "status-pending",
                "estado_texto": item.get("estado_reserva", "Pendiente"),
                "equipo": f"Artículo ID: {item.get('id_reservado')}",
                "fecha": item.get("fecha_retiro", "Desconocida"),
                "ubicacion": "Sede FIUBA",
                "acciones": ["Cancelar", "Ver QR"]
            })
        estadisticas = {"actuales": len(reservas_api), "historicas": 14, "sanciones": 0}
    except Exception:
        # Mock Fallback
        reservas_api = [
            {
                "id": 1,
                "estado_clase": "status-active",
                "estado_texto": "Lista para retiro (Mock)",
                "equipo": "Proyector Epson WXGA",
                "fecha": "Hoy, 18:00 - 20:00 hs",
                "ubicacion": "Sede Paseo Colón - Aula 204",
                "acciones": ["Cancelar", "Ver QR"]
            },
            {
                "id": 2,
                "estado_clase": "status-pending",
                "estado_texto": "En curso (Mock)",
                "equipo": "Notebook Dell Latitude",
                "fecha": "Hoy, 15:00 - 18:00 hs",
                "ubicacion": "Retirado (En posesión)",
                "acciones": ["Reportar Fallo", "Extender Plazo"]
            }
        ]
        estadisticas = {"actuales": 2, "historicas": 14, "sanciones": 0}

    return render_template("profesor/dashboard.html", reservas=reservas_api, estadisticas=estadisticas)


@profesor_bp.route("/nueva", methods=["GET"])
def nueva_reserva():
    """Renderiza el formulario para crear una nueva reserva.

    Returns:
        str: Plantilla HTML del formulario de nueva reserva.
    """
    return render_template("profesor/nueva_reserva.html")


@profesor_bp.route("/guardar", methods=["POST"])
def guardar_reserva():
    """Lógica para guardar la nueva reserva en el sistema.

    Returns:
        Response: Redirección al panel de control.
    """
    return redirect("/dashboard")


from datetime import datetime

BACKEND_URL = "http://127.0.0.1:5001"

@profesor_bp.route("/historial", methods=["GET"])
def historial():
    "Muestra el historial completo de reservas historicas de un profesor"

    id_profesor = request.args.get('id')
    token = request.headers.get('Authorization')
    headers = {'Authorization': token}

    try:
        response = requests.get(f"{BACKEND_URL}/users/{id_profesor}/loans", headers=headers)
        if response.status_code == 200:
            reservas_totales = response.json()
            hoy = datetime.now()
            historial = []

            for reserva in reservas_totales:
                fecha_fin = datetime.strptime(reserva["fecha_fin"], '%Y-%m-%d %H:%M:%S')
                if fecha_fin < hoy:
                    historial.append(reserva)

            return render_template("profesor/historial_reservas.html", historial=historial)
        else:
            return render_template("profesor/historial_reservas.html", historial=[], error="No se pudo obtener el historial")
        
    except Exception as e:
        print(f"Error inesperado: {e}")
        return render_template("profesor/historial_reservas.html", historial=[], error="Error al mostrar el historial")
