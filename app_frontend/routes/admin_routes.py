"""Rutas del area de administracion."""

import config
import requests
from flask import Blueprint, render_template, session, redirect, url_for, request
from services.api_client import obtener_detalle_prestamo
from http_codes_and_messages import (
    HTTP_OK,
    HTTP_NOT_FOUND,
    HTTP_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
    MSG_INTERNAL_SERVER_ERROR,
)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/prestamos/<int:id>")
def prestamo_detalle(id):
    """Renderiza la vista de detalle de préstamo para administradores.

    Args:
        id (int): El ID único del préstamo.

    Returns:
        str: Plantilla HTML renderizada con los datos mapeados del préstamo.
    """
    try:
        datos_api = obtener_detalle_prestamo(id)
        prestamo = {
            "id": datos_api.get("id", id),
            "estado_general": datos_api.get("estado_reserva", "pendiente"),
            "estado_texto": datos_api.get("estado_reserva", "Pendiente"),
            "estado_clase": "status-pending" if datos_api.get("estado_reserva") == "pendiente" else "status-active",
            "equipo_nombre": datos_api.get("nombre_art", "Material no especificado"),
            "equipo_id": datos_api.get("id_reservado", "N/A"),
            "titular_nombre": datos_api.get("nombre", "Alumno"),
            "titular_legajo": datos_api.get("id_usuario", "N/A"),
            "titular_carrera": "No definida",
            "fecha_retiro": datos_api.get("fecha_retiro", "N/A"),
            "fecha_limite": datos_api.get("fecha_regreso", "N/A")
        }
    except Exception:
        # Mock Fallback
        prestamo = {
            "id": id,
            "estado_general": "en_curso",
            "estado_texto": "En curso (Retirado)",
            "estado_clase": "status-pending",
            "equipo_nombre": "Proyector Epson WXGA",
            "equipo_id": "PRJ-012",
            "titular_nombre": "Juan Pérez",
            "titular_legajo": "102345",
            "titular_carrera": "Ingeniería Informática",
            "fecha_retiro": "15 May 2026 - 15:00 hs",
            "fecha_limite": "15 May 2026 - 18:00 hs"
        }
        
    return render_template("admin/prestamo_detalle.html", prestamo=prestamo)


@admin_bp.route("/articulos")
def listar_articulos():
    """Renderiza la vista de listado de artículos para administradores.

    Returns:
        str: Plantilla HTML renderizada con los artículos.
    """
    return render_template("admin/articulos.html")


@admin_bp.route("/articulos/nuevo")
def crear_articulo():
    """Renderiza la vista de creación de nuevo artículo para administradores.

    Returns:
        str: Plantilla HTML del formulario de artículo.
    """
    return render_template("admin/articulos_form.html")


@admin_bp.route("/dashboard")
def dashboard():
    """Renderiza la vista del dashboard para administradores.

    Returns:
        str: Plantilla HTML del panel principal del administrador.
    """
    return render_template("admin/dashboard.html")


# Rutas adicionales provenientes de la versión blueprint (ajustadas al url_prefix)
@admin_bp.route('/usuarios/<id>/editar', methods=['POST'])
def editar_usuario(id):
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    response = requests.put(f"http://localhost:5001/api/users/{id}", json=request.form.to_dict(), headers={"Authorization": f"Bearer {token}"})
    if response.status_code == HTTP_OK:
        return redirect(url_for('admin.obtener_usuario', id=id))
    elif response.status_code == HTTP_NOT_FOUND:
        return render_template("404.html", message=MSG_NOT_FOUND), HTTP_NOT_FOUND
    else:
        return render_template("500.html", message=MSG_INTERNAL_SERVER_ERROR), HTTP_INTERNAL_SERVER_ERROR

@admin_bp.route('/usuarios/<id>', methods=['GET'])
def obtener_usuario(id):
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    response = requests.get(f"http://localhost:5001/api/users/{id}", headers={"Authorization": f"Bearer {token}"})
    if response.status_code == HTTP_OK:
        usuario = response.json()
        return render_template("admin/perfil_usuario.html", usuario=usuario)
    elif response.status_code == HTTP_NOT_FOUND:
        return render_template("404.html", message=MSG_NOT_FOUND), HTTP_NOT_FOUND
    else:
        return render_template("500.html", message=MSG_INTERNAL_SERVER_ERROR), HTTP_INTERNAL_SERVER_ERROR
