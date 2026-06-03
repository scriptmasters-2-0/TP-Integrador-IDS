"""Rutas del area de alumnos."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from services.api_client import get_json, post_json


alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")


@alumno_bp.route("/perfil")
def perfil():
    """Renderiza la pagina de perfil del alumno."""
    return render_template("alumno/perfil.html", perfil=session.get("user", {}))


@alumno_bp.route("/historial")
def historial():
    """Renderiza el historial de prestamos del alumno."""
    token = session.get("token")
    user_id = (session.get("user") or {}).get("id")

    loans = []
    error = None
    if user_id:
        payload, error = get_json(f"/api/users/{user_id}/loans", token=token)
        if isinstance(payload, list):
            loans = payload

    return render_template("alumno/historial.html", loans=loans, fetch_error=error)


@alumno_bp.route("/mis-reservas/nueva", methods=["GET", "POST"])
def nueva_reserva():
    """Renderiza y procesa el formulario de nueva reserva para alumnos."""
    token = session.get("token")
    user_id = (session.get("user") or {}).get("id")

    if request.method == "POST":
        item_id = request.form.get("articulo")
        if user_id and item_id:
            post_json(
                "/api/loans",
                {"user_id": user_id, "item_id": item_id},
                token=token,
            )
        return redirect(url_for("alumno.historial"))

    items_payload, fetch_error = get_json("/api/items", token=token)
    items = items_payload if isinstance(items_payload, list) else []

    return render_template(
        "alumno/nueva_reserva.html",
        items=items,
        fetch_error=fetch_error,
    )


@alumno_bp.route("/prestamos/id/comprobante")
def comprobante():
    """Renderiza el comprobante de un prestamo especifico para el alumno."""
    return render_template("alumno/comprobante.html")
