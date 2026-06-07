"""Rutas del area de profesores."""


from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios import articulos_servicio, reservas_servicio
from servicios.api_client import get_json
from servicios.reservas_servicio import obtener_qr_reserva

profesor_bp = Blueprint("profesor", __name__, url_prefix="/profesor")


@profesor_bp.route("/perfil")
def perfil():
    """Renderiza la vista de perfil del profesor."""
    return render_template("profesor/perfil.html", perfil=session.get("usuario", {}))


@profesor_bp.route("/dashboard")
def dashboard():
    """Renderiza el panel de control del profesor."""
    token = session.get("token")
    usuario_id = (session.get("usuario") or {}).get("id")

    reservas = []
    error = None
    if usuario_id:
        payload, error = get_json(f"/usuarios/{usuario_id}/reservas", token=token)
        if isinstance(payload, list):
            for articulo in payload:
                reservas.append(
                    {
                        "id": articulo.get("id"),
                        "estado_clase": "status-active"
                        if articulo.get("estado_reserva") != "pendiente"
                        else "status-pending",
                        "estado_texto": articulo.get("estado_reserva", "Pendiente"),
                        "equipo": articulo.get(
                            "nombre_art", f"Artículo {articulo.get('id_reservado') or ''}"
                        ),
                        "fecha": articulo.get("fecha_retiro", "Desconocida"),
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


"""@profesor_bp.route("/historial")
def historial():
    Alias temporal para historial del profesor.
    return dashboard()"""


@profesor_bp.route("/nueva", methods=["GET"])
def nueva_reserva():
    """Renderiza el formulario para crear una nueva reserva."""
    articulos = articulos_servicio.obtener_articulos()

    return render_template(
        "profesor/nueva_reserva.html",
        articulos=articulos,
    )


@profesor_bp.route("/guardar", methods=["POST"])
def guardar_reserva():
    """Lógica para guardar la nueva reserva."""
    usuario_id = (session.get("usuario") or {}).get("id")
    articulo_id = request.form.get("articulo")

    if usuario_id and articulo_id:
        reservas_servicio.crear_reserva({"usuario_id": usuario_id, "articulo_id": articulo_id})

    return redirect(url_for("profesor.mis_reservas"))


@profesor_bp.route("/historial", methods=["GET"])
def historial_reserva():
    """Muestra el historial completo de reservas historicas de un profesor."""
    usuario, error = get_json("/auth/me")

    if error:
        return render_template(
            "profesor/historial_reservas.html", reservas=[], error=error
        )

    usuario_id = usuario["usuario"]["id"]
    reservas, error = get_json(f"/usuarios/{usuario_id}/reservas")

    return render_template(
        "profesor/historial_reservas.html", reservas=reservas or [], error=error
    )


@profesor_bp.route("/reservas/<int:id>/comprobante", methods=["GET"])
def comprobante(id):
    """Muestra el comprobante de reserva."""
    qr, error = obtener_qr_reserva(id)

    return render_template("profesor/comprobante.html", qr=qr)
