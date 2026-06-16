"""Rutas del área del bibliotecario."""

from flask import Blueprint, request, redirect, session, url_for, render_template, jsonify

from servicios.reservas_servicio import establecer_estado_reserva, obtener_solicitudes, escanear_qr_reserva

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


@biblio_bp.route("/scan", methods=["GET"])
def abrir_escaner():

    token = session.get("token")
    rol = session.get("rol") 

    if not token or rol != "bibliotecario":
        return redirect(url_for("public.login"))
    
    return render_template("biblioteca/escanear_qr.html")


@biblio_bp.route("/reservas/<int:id_reserva>/scan", methods=["PATCH"])
def escanear_reserva(id_reserva):
    """Escanea una reserva y cambia su estado.
    estado: entregado al escanear por primera vez en el retiro del articulo
    estado: devuelto al escanear por segunda vez en la devolucion"""

    token = session.get("token")

    if not token:
        return redirect(url_for("public.login"))
    
    escaneo, error = escanear_qr_reserva(id_reserva, token)

    if error:
        return jsonify({"error": error}), 400
    
    return jsonify(escaneo), 200