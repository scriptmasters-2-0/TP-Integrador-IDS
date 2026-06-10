"""Rutas del area de profesores."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios import articulos_servicio, reservas_servicio
from servicios.api_client import get_json
from servicios.fechas_servicio import formatear_fecha_argentina
from servicios.paginacion_servicio import DEFAULT_PER_PAGE, paginar_lista
from servicios.reservas_servicio import obtener_qr_reserva, establecer_estado_reserva
from servicios.usuario_servicio import obtener_reservas_usuario_con_error

profesor_bp = Blueprint("profesor", __name__, url_prefix="/profesor")


@profesor_bp.route("/perfil")
def perfil():
    """Renderiza la vista de perfil del profesor."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))
    mensaje = request.args.get("mensaje")
    return render_template("profesor/perfil.html", perfil=session.get("usuario", {}), mensaje=mensaje)

@profesor_bp.route("/cambiar_contrasena", methods=["POST"])
def cambiar_contrasena():
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    nueva_contrasena = request.form.get("nueva_contrasena")
    usuario_id = usuario.get("id")

    from servicios.usuario_servicio import actualizar_usuario
    actualizar_usuario(usuario_id, {"contrasenia": nueva_contrasena}, token=token)

    return redirect(url_for("profesor.perfil", mensaje="Contraseña actualizada exitosamente"))

@profesor_bp.route("/dashboard")
def dashboard():
    """Renderiza el panel de control del profesor."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))
    usuario_id = (session.get("usuario") or {}).get("id")

    payload, error = obtener_reservas_usuario_con_error(usuario_id, token=token)

    reservas = []
    total_activas = 0
    total_historicas = 0

    if not error and isinstance(payload, list):
        for reserva in payload:
            estado = reserva.get("estado_reserva", "")
            entrada = {
                "id": reserva.get("id"),
                "estado_clase": "status-pending" if estado == "pendiente" else "status-active",
                "estado_texto": estado,
                "equipo": reserva.get("nombre_art") or f"Artículo {reserva.get('id_reservado') or ''}",
                "fecha": reserva.get("fecha_retiro", "Desconocida"),
                "ubicacion": "Sede FIUBA",
            }
            if estado in ("pendiente", "aprobado", "entregado"):
                reservas.append(entrada)
                total_activas += 1
            else:
                total_historicas += 1

    estadisticas = {
        "actuales": total_activas,
        "historicas": total_historicas,
    }

    return render_template(
        "profesor/dashboard.html",
        reservas=reservas,
        estadisticas=estadisticas,
        fetch_error=error,
    )

@profesor_bp.route("/mis-reservas")
def mis_reservas():
    """Vista de reservas activas e historial del profesor con tabs."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))

    usuario_id = (session.get("usuario") or {}).get("id")
    payload, error = obtener_reservas_usuario_con_error(usuario_id, token=token)

    reservas_activas = []
    reservas_historicas = []

    if not error and isinstance(payload, list):
        for reserva in payload:
            estado = reserva.get("estado_reserva", "")
            entrada = {
                "id": reserva.get("id"),
                "nombre_articulo": (
                    reserva.get("nombre_articulo")
                    or reserva.get("nombre_art")
                    or "Artículo"
                ),
                "estado_reserva": estado,
                "fecha_retiro": formatear_fecha_argentina(reserva.get("fecha_retiro")),
                "fecha_regreso": formatear_fecha_argentina(reserva.get("fecha_regreso")),
            }
            if estado in ("pendiente", "aprobado", "entregado"):
                reservas_activas.append(entrada)
            else:  
                reservas_historicas.append(entrada)

    return render_template(
        "profesor/mis-reservas.html",
        reservas_activas=reservas_activas,
        reservas_historicas=reservas_historicas,
        fetch_error=error,
    )

@profesor_bp.route("/prestamos/<int:id>", methods=["GET"])
def detalle_reserva(id):
    """Detalle de un préstamo específico del profesor."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))

    datos_api, error = get_json(f"/reservas/{id}", token=token)

    reserva = None
    if not error and datos_api:
        reserva = {
            "id": datos_api.get("id", id),
            "estado_reserva": datos_api.get("estado_reserva", "N/A"),
            "fecha_retiro": datos_api.get("fecha_retiro", "N/A"),
            "fecha_regreso": datos_api.get("fecha_regreso", "N/A"),
            "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=FIUBA-RES-{id}",
        }

    return render_template(
        "profesor/detalle_reserva.html",
        reserva=reserva,
        fetch_error=error,
    )


@profesor_bp.route("/nueva", methods=["GET"])
def nueva_reserva():
    """Renderiza el formulario para crear una nueva reserva."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))
    articulos = articulos_servicio.obtener_articulos()

    return render_template(
        "profesor/nueva_reserva.html",
        articulos=articulos,
    )


@profesor_bp.route("/guardar", methods=["POST"])
def guardar_reserva():
    """Lógica para guardar la nueva reserva."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))
    usuario_id = (session.get("usuario") or {}).get("id")
    articulo_id = request.form.get("articulo")

    if usuario_id and articulo_id:
        reservas_servicio.crear_reserva({"usuario_id": usuario_id, "articulo_id": articulo_id})

    return redirect(url_for("profesor.mis_reservas"))


@profesor_bp.route("/historial", methods=["GET"])
def historial_reserva():
    """Muestra el historial completo de reservas históricas de un profesor."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))

    usuario_id = (session.get("usuario") or {}).get("id")
    payload, error = obtener_reservas_usuario_con_error(usuario_id, token=token)

    reservas_formateadas = []
    if not error and isinstance(payload, list):
        for reserva in payload:
            reservas_formateadas.append({
                "id": reserva.get("id"),
                "nombre_articulo": (
                    reserva.get("nombre_articulo")
                    or reserva.get("nombre_art")
                    or "Artículo"
                ),
                "estado_reserva": reserva.get("estado_reserva", "pendiente"),
                "fecha_regreso": formatear_fecha_argentina(reserva.get("fecha_regreso")),
            })

    page = request.args.get("page", 1, type=int) or 1
    reservas_formateadas, pagination = paginar_lista(
        reservas_formateadas,
        pagina=page,
        por_pagina=DEFAULT_PER_PAGE,
    )

    return render_template(
        "profesor/historial_reservas.html",
        reservas=reservas_formateadas,
        pagination=pagination,
        fetch_error=error,
    )


@profesor_bp.route("/reservas/<int:id>/comprobante", methods=["GET"])
def comprobante(id):
    """Muestra el comprobante de reserva."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))
    qr, error = obtener_qr_reserva(id)

    return render_template("profesor/comprobante.html", qr=qr)


@profesor_bp.route("/profesor-mis-reservas")
def profesor_mis_reservas():
    """Alias legacy para mis reservas del profesor."""
    return redirect(url_for("profesor.mis_reservas"))


@profesor_bp.route("/reservas/<int:id>/cancelar-profesor", methods=["POST"])
def profesor_cancelar_reserva(id):
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))

    establecer_estado_reserva(id, {"estado_reserva": "cancelado"})
    return redirect(url_for("profesor.mis_reservas"))