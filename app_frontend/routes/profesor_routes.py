"""Rutas del area de profesores."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios import articulos_servicio, reservas_servicio
from servicios.fechas_servicio import formatear_fecha_argentina
from servicios.paginacion_servicio import DEFAULT_PER_PAGE, paginar_lista
from servicios.reservas_servicio import establecer_estado_reserva, obtener_qr_reserva
from servicios.usuario_servicio import actualizar_usuario, obtener_reservas_usuario

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

    payload, error, status = actualizar_usuario(
        usuario_id, {"contrasenia": nueva_contrasena}, token=token
    )
    if error:
        return redirect(url_for("profesor.perfil", mensaje="No se pudo actualizar la contraseña."))

    return redirect(url_for("profesor.perfil", mensaje="Contraseña actualizada exitosamente"))

@profesor_bp.route("/dashboard")
def dashboard():
    """Renderiza el panel de control del profesor."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))
    usuario_id = (session.get("usuario") or {}).get("id")

    payload, error = obtener_reservas_usuario(usuario_id, token=token)

    reservas = []
    total_activas = 0
    total_historicas = 0

    if not error and isinstance(payload, list):
        for reserva in payload:
            estado = reserva.get("estado_reserva", "")
            entrada = {
                "id": reserva.get("id"),
                "estado_clase": reservas_servicio.status_class(estado),
                "estado_texto": estado,
                "equipo": reserva.get("nombre_art") or f"Artículo {reserva.get('id_reservado') or ''}",
                "fecha": formatear_fecha_argentina(reserva.get("fecha_retiro")),
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
        reservas=reservas[:3],
        estadisticas=estadisticas,
        fetch_error=error,
        mostrar_ver_mas_reservas=total_activas > 3,
    )

@profesor_bp.route("/historial", methods=["GET"])
def historial_reserva():
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))

    usuario_id = (session.get("usuario") or {}).get("id")
    payload, error = obtener_reservas_usuario(usuario_id, token=token)

    q = (request.args.get("q") or "").strip().lower()
    estado_filtro = (request.args.get("estado") or "").strip()

    reservas_formateadas = []
    estados_vistos = set()

    if not error and isinstance(payload, list):
        for reserva in payload:
            estado = reserva.get("estado_reserva", "pendiente")
            estados_vistos.add(estado)
            nombre = (
                reserva.get("nombre_articulo")
                or reserva.get("nombre_art")
                or "Artículo"
            )
            reservas_formateadas.append({
                "id": reserva.get("id"),
                "nombre_articulo": nombre,
                "estado_reserva": estado,
                "estado_clase": reservas_servicio.badge_class(estado),
                "fecha_regreso": formatear_fecha_argentina(reserva.get("fecha_regreso")),
            })

    if q:
        reservas_formateadas = [r for r in reservas_formateadas if q in r["nombre_articulo"].lower()]
    if estado_filtro:
        reservas_formateadas = [r for r in reservas_formateadas if r["estado_reserva"] == estado_filtro]

    page = request.args.get("page", 1, type=int) or 1
    reservas_formateadas, pagination = paginar_lista(
        reservas_formateadas, pagina=page, por_pagina=DEFAULT_PER_PAGE,
    )

    return render_template(
        "profesor/historial_reservas.html",
        reservas=reservas_formateadas,
        fetch_error=error,
        pagination=pagination,
        estado_opciones=sorted(estados_vistos),
        filtros={"q": q, "estado": estado_filtro},
    )

@profesor_bp.route("/prestamos/<int:id>", methods=["GET"])
def detalle_reserva(id):
    """Detalle de un préstamo específico del profesor."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))

    datos_api, error = reservas_servicio.obtener_reserva(id, token=token)

    reserva = None
    if not error and datos_api:
        qr, qr_error = obtener_qr_reserva(id, token=token)
        reserva = {
            "id": datos_api.get("id", id),
            "estado_reserva": datos_api.get("estado_reserva", "N/A"),
            "estado_clase": reservas_servicio.badge_class(
                datos_api.get("estado_reserva")
            ),
            "fecha_retiro": formatear_fecha_argentina(datos_api.get("fecha_retiro")),
            "fecha_regreso": formatear_fecha_argentina(datos_api.get("fecha_regreso")),
            "qrData": (qr or {}).get("qrData"),
        }
        error = error or qr_error

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
    articulos = articulos_servicio.obtener_articulos(params={"disponible": "true", "limit": 100}, token=token)

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
    fecha = request.form.get("fecha")
    desde = request.form.get("desde")
    hasta = request.form.get("hasta")

    if usuario_id and articulo_id:
        reserva_data = {"usuario_id": usuario_id, "articulo_id": articulo_id}
        if fecha and desde and hasta:
            reserva_data.update(
                {
                    "fecha_retiro": f"{fecha} {desde}:00",
                    "hora_regreso": f"{hasta}:00",
                }
            )
        payload, error, status = reservas_servicio.crear_reserva(
            reserva_data,
            token=token,
        )
        if error:
            return redirect(
                url_for(
                    "profesor.mis_reservas",
                    mensaje_error="No se pudo crear la reserva.",
                )
            )

    return redirect(url_for("profesor.mis_reservas"))

@profesor_bp.route("/mis-reservas")
def mis_reservas():
    """Vista de reservas activas e historial del profesor con tabs."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))

    mensaje_error = request.args.get("mensaje_error")
    usuario_id = (session.get("usuario") or {}).get("id")
    payload, error = obtener_reservas_usuario(usuario_id, token=token)

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
                "estado_clase": reservas_servicio.badge_class(estado),
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
        mensaje_error=mensaje_error,
    )

@profesor_bp.route("/reservas/<int:id>/comprobante", methods=["GET"])
def comprobante(id):
    """Muestra el comprobante de reserva."""
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))

    datos_api, error = reservas_servicio.obtener_reserva(id, token=token)

    if error:
        return render_template(
            "profesor/comprobante.html",
            qr=None,
            fetch_error=error
        )

    if datos_api.get("estado_reserva") not in ["aprobado", "entregado"]:
        return render_template(
            "profesor/comprobante.html",
            qr=None,
            acceso_denegado=True
        )

    qr, error = obtener_qr_reserva(id, token=token)

    return render_template("profesor/comprobante.html", qr=qr, acceso_denegado=False)


@profesor_bp.route("/profesor-mis-reservas")
def profesor_mis_reservas():
    """Alias legacy para mis reservas del profesor."""
    return redirect(url_for("profesor.mis_reservas"))


@profesor_bp.route("/reservas/<int:id>/cancelar-profesor", methods=["POST"])
def profesor_cancelar_reserva(id):
    token = session.get("token")
    if not token or session.get("rol") != "profesor":
        return redirect(url_for("public.login"))

    cancelada, error, status = establecer_estado_reserva(
        id, {"estado_reserva": "cancelado"}, token=token
    )
    if error or not cancelada:
        return redirect(
            url_for(
                "profesor.mis_reservas",
                mensaje_error="No se pudo cancelar la reserva.",
            )
        )
    return redirect(url_for("profesor.mis_reservas"))
