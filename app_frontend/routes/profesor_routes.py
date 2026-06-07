"""Rutas del area de profesores."""

from datetime import datetime

from flask import Blueprint, redirect, render_template, request, session, url_for

from config import BACKEND_URL
from services import items_service, loans_service
from services.api_client import get_json, post_json
from services.user_service import obtener_prestamos_usuario
from services.loans_service import obtener_qr_reserva

profesor_bp = Blueprint("profesor", __name__, url_prefix="/profesor")


@profesor_bp.route("/perfil")
def perfil():
    """Renderiza la vista de perfil del profesor."""
    return render_template("profesor/perfil.html", perfil=session.get("user", {}))


@profesor_bp.route("/dashboard")
def dashboard():
    """Renderiza el panel de control del profesor."""
    token = session.get("token")
    user_id = (session.get("user") or {}).get("id")

    reservas = []
    error = None
    if user_id:
        payload, error = get_json(f"/users/{user_id}/loans", token=token)
        if isinstance(payload, list):
            for item in payload:
                reservas.append(
                    {
                        "id": item.get("id"),
                        "estado_clase": "status-active"
                        if item.get("estado_reserva") != "pendiente"
                        else "status-pending",
                        "estado_texto": item.get("estado_reserva", "Pendiente"),
                        "equipo": item.get(
                            "nombre_art", f"Artículo {item.get('id_reservado') or ''}"
                        ),
                        "fecha": item.get("fecha_retiro", "Desconocida"),
                        "ubicacion": "Sede FIUBA",
                        "acciones": ["Cancelar", "Ver QR"],
                    }
                )

    estadisticas = {
        "actuales": len(reservas),
        "historicas": 0,
        "sanciones": 0,
    }

    return render_template(
        "profesor/dashboard.html",
        reservas=reservas,
        estadisticas=estadisticas,
        fetch_error=error,
    )


@profesor_bp.route("/mis-reservas")
def mis_reservas():
    """Alias amigable para la vista de reservas del profesor."""
    return dashboard()


@profesor_bp.route("/historial")
def historial():
    """Alias temporal para historial del profesor."""
    return dashboard()


@profesor_bp.route("/nueva", methods=["GET"])
def nueva_reserva():
    """Renderiza el formulario para crear una nueva reserva."""
    items = items_service.obtener_items()

    return render_template(
        "profesor/nueva_reserva.html",
        items=items,
    )


@profesor_bp.route("/guardar", methods=["POST"])
def guardar_reserva():
    """Lógica para guardar la nueva reserva."""
    user_id = (session.get("user") or {}).get("id")
    item_id = request.form.get("articulo")

    if user_id and item_id:
        loans_service.crear_prestamo({"user_id": user_id, "item_id": item_id})

    return redirect(url_for("profesor.mis_reservas"))


@profesor_bp.route("/historial", methods=["GET"])
def historial_reserva():
    "Muestra el historial completo de reservas historicas de un profesor"

    rol = session.get("profesor")
    """if rol not in ["profesor"]:
        return redirect("/")"""
    
    """user_id = session.get("user_id")"""
    prestamos = obtener_prestamos_usuario(3) 

    return render_template("/historial_reservas.html", prestamos=prestamos)


@profesor_bp.route("/prestamos/<int:id>/comprobante", methods=["GET"])
def comprobante(id):
    """Muestra el comprobante de reserva"""

    qr, error = obtener_qr_reserva(id)
    
    return render_template("/profesor/comprobante.html", qr=qr)
