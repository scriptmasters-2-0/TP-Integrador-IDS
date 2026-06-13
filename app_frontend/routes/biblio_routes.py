"""Rutas del área del bibliotecario."""

from flask import Blueprint, request, redirect, session, url_for, render_template

from servicios.reservas_servicio import establecer_estado_reserva, obtener_solicitudes

biblio_bp = Blueprint("biblioteca", __name__, url_prefix="/biblioteca")

@biblio_bp.route("/reservas/solicitudes", methods=["GET"])
def listar_pendientes():
    """Obtiene todas las reservas con estado pendiente."""
    
    reservas_pendientes = obtener_solicitudes()

    return render_template(
        "/biblioteca/solicitudes_reservas.html",
        reservas=reservas_pendientes
    )


@biblio_bp.route("/reservas/solicitudes/<int:id_reserva>", methods=["POST"])
def modificar_estado(id_reserva):
    """Acepta o rechaza una solicitud de reserva."""
    estado_a_modificar = request.form.get("estado_reserva")

    establecer_estado_reserva(id_reserva, {"estado_reserva": estado_a_modificar})

    return redirect(url_for("biblioteca.listar_pendientes"))
