"""Rutas del area de alumnos."""

import logging

from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios import articulos_servicio, penalizaciones_servicio, reservas_servicio
from servicios.fechas_servicio import formatear_fecha_argentina
from servicios.historial_filtros_servicio import (
    estados_disponibles,
    filtrar_historial_reservas,
)
from servicios.paginacion_servicio import DEFAULT_PER_PAGE, paginar_lista
from servicios.usuario_servicio import (
    obtener_reservas_usuario,
    actualizar_usuario,
)
from servicios.auth_servicio import obtener_mi_perfil

logger = logging.getLogger(__name__)
alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")


@alumno_bp.route("/perfil")
def perfil():
    """Renderiza la página de perfil del alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    mensaje = request.args.get("mensaje")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    try:
        perfil_fresco = obtener_mi_perfil(token=token)
        if perfil_fresco and "usuario" in perfil_fresco:
            usuario = perfil_fresco["usuario"]
    except Exception:
        logger.exception("Error al obtener el perfil del usuario")

    return render_template("alumno/perfil.html", usuario=usuario, mensaje=mensaje)

@alumno_bp.route("/cambiar_contrasena", methods=["POST"])
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
        return redirect(url_for("alumno.perfil", mensaje="No se pudo actualizar la contraseña."))
    
    return redirect(url_for("alumno.perfil", mensaje="Contraseña actualizada exitosamente"))


@alumno_bp.route("/historial")
def historial():
    """Renderiza el historial de préstamos del alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))
    usuario_id = usuario.get("id")
    filtros = {
        "q": (request.args.get("q") or "").strip(),
        "estado": (request.args.get("estado") or "").strip(),
        "fecha_desde": (request.args.get("fecha_desde") or "").strip(),
        "fecha_hasta": (request.args.get("fecha_hasta") or "").strip(),
    }
    filtros_activos = any(filtros.values())
    filtros_url = {clave: valor for clave, valor in filtros.items() if valor}

    historial_datos = []
    payload, error = obtener_reservas_usuario(usuario_id, token=token)
    if usuario_id and not error and isinstance(payload, list):
        for reserva in payload:
            nombre_articulo = (
                reserva.get("nombre_articulo")
                or reserva.get("nombre_art")
                or "Artículo no disponible"
            )
            estado_reserva = reserva.get("estado_reserva") or "desconocido"
            historial_datos.append(
                {
                    "id": reserva.get("id", 1),
                    "fecha": formatear_fecha_argentina(reserva.get("fecha_retiro")),
                    "fecha_filtro": reserva.get("fecha_retiro"),
                    "nombre_equipo": nombre_articulo,
                    "id_equipo": reserva.get("id_reservado"),
                    "sede": reserva.get("seccion", "Sede FIUBA"),
                    "estado_texto": estado_reserva,
                    "estado_clase": reservas_servicio.badge_class(estado_reserva),
                }
            )

    total_historial = len(historial_datos)
    estado_opciones = estados_disponibles(historial_datos)
    historial_datos, filter_error = filtrar_historial_reservas(historial_datos, filtros)

    page = request.args.get("page", 1, type=int) or 1
    historial_datos, pagination = paginar_lista(
        historial_datos,
        pagina=page,
        por_pagina=DEFAULT_PER_PAGE,
    )

    return render_template(
        "alumno/historial.html",
        historial=historial_datos,
        fetch_error=error,
        filtros=filtros,
        filtros_activos=filtros_activos,
        filtros_url=filtros_url,
        filter_error=filter_error,
        estado_opciones=estado_opciones,
        total_historial=total_historial,
        pagination=pagination,
    )


@alumno_bp.route("/mis-reservas/nueva", methods=["GET", "POST"])
def nueva_reserva():
    """Renderiza y procesa el formulario de nueva reserva para alumnos."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))
    usuario_id = usuario.get("id")

    if request.method == "POST":
        articulo_id = request.form.get("articulo_id")
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
                        "alumno.alumno_mis_reservas",
                        mensaje_error="No se pudo crear la reserva.",
                    )
                )
        return redirect(url_for("alumno.historial"))

    articulos = articulos_servicio.obtener_articulos(params={"disponible": "true", "limit": 100}, token=token)
    fetch_error = None

    articulo_preseleccionado = request.args.get("articulo_id", type=int)

    return render_template(
        "alumno/nueva_reserva.html",
        articulos=articulos,
        articulo_preseleccionado=articulo_preseleccionado,
        fetch_error=fetch_error,
    )


@alumno_bp.route("/reservas/<int:id>/comprobante")
def comprobante(id):
    """Renderiza el comprobante de una reserva específica para el alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    try:
        datos_api = reservas_servicio.obtener_detalle_reserva(id, token=token)
        
        reserva = {
            "id": datos_api.get("id", id),
            "estado_texto": datos_api.get("estado_reserva", "pendiente"),
            "estado_clase": reservas_servicio.status_class(
                datos_api.get("estado_reserva", "pendiente")
            ),
            "equipo_nombre": datos_api.get("nombre_art", "Material no especificado"),
            "equipo_id": datos_api.get("id_reservado", "N/A"),
            "sede": datos_api.get("seccion", "Sede Central FIUBA"),
            "fecha_reserva": formatear_fecha_argentina(datos_api.get("fecha_retiro")),
            "fecha_retiro": formatear_fecha_argentina(datos_api.get("fecha_retiro")),
            "fecha_limite": formatear_fecha_argentina(datos_api.get("fecha_regreso")),
            "titular_nombre": datos_api.get("nombre", "Alumno"),
            "titular_legajo": datos_api.get("id_usuario", "N/A"),
        }
        qr, qr_error = reservas_servicio.obtener_qr_reserva(id, token=token)
    except Exception:
        logger.exception("Error al obtener el detalle de la reserva con ID %s", id)
        reserva = {
            "id": id,
            "estado_texto": "Error al cargar",
            "estado_clase": "status-error",
            "equipo_nombre": "No disponible",
            "equipo_id": "N/A",
            "sede": "No especificada",
            "fecha_reserva": "N/A",
            "fecha_retiro": "N/A",
            "fecha_limite": "N/A",
            "titular_nombre": "Usuario",
            "titular_legajo": "N/A",
        }
        qr = None
        qr_error = "No se pudo obtener el QR de la reserva."

    return render_template(
        "alumno/comprobante.html",
        reserva=reserva,
        qr=qr or {},
        fetch_error=qr_error,
    )


@alumno_bp.route("/dashboard")
def dashboard():
    """Panel principal: reservas activas y alertas de penalización."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    mensaje_error = request.args.get("mensaje_error")
    usuario_id = usuario.get("id")
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
                "equipo": (
                    reserva.get("nombre_articulo")
                    or reserva.get("nombre_art")
                    or "Artículo no disponible"
                ),
                "fecha": formatear_fecha_argentina(reserva.get("fecha_retiro")),
                "ubicacion": reserva.get("seccion", "Sede FIUBA"),
            }
            if estado in ("pendiente", "aprobado", "entregado"):
                reservas.append(entrada)
                total_activas += 1
            else:
                total_historicas += 1

    penalizaciones = usuario.get("penalizaciones")
    penalizaciones = penalizaciones if isinstance(penalizaciones, list) else []
    estadisticas = {
        "actuales": total_activas,
        "historicas": total_historicas,
        "penalizaciones": len(penalizaciones),
    }

    return render_template(
        "alumno/dashboard.html",
        reservas=reservas,
        estadisticas=estadisticas,
        penalizaciones=penalizaciones,
        fetch_error=error,
        mensaje_error=mensaje_error,
    )


@alumno_bp.route("/reservas/<int:id>", methods=["GET"])
def reserva_detalle(id):
    """Detalle de reserva: estado, fecha retiro/regreso, QR."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    datos_api, error = reservas_servicio.obtener_reserva(id, token=token)

    if error:
        return render_template(
            "alumno/reserva_detalle_alumno.html", 
            reserva=None, 
            fetch_error=error
        )

    if datos_api.get("estado_reserva") not in ["aprobado", "entregado"]:
        return render_template(
            "alumno/reserva_detalle_alumno.html", 
            reserva=None, 
            acceso_denegado=True
        )
        
    qr, qr_error = reservas_servicio.obtener_qr_reserva(id, token=token)

    reserva = {
        "id": datos_api.get("id"),
        "estado": datos_api.get("estado_reserva"),
        "fecha_retiro": formatear_fecha_argentina(datos_api.get("fecha_retiro")),
        "fecha_regreso": formatear_fecha_argentina(datos_api.get("fecha_regreso")),
        "qrData": (qr or {}).get("qrData"),
    }

    return render_template(
        "alumno/reserva_detalle_alumno.html",
        reserva=reserva,
        fetch_error=qr_error,
    )

@alumno_bp.route("/penalizaciones")
def alumno_penalizaciones():
    """Renderiza las penalizaciones activas del alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    usuario_id = usuario.get("id")
    penalizaciones, error = penalizaciones_servicio.obtener_penalizaciones(
        params={"usuario_id": usuario_id},
        token=token,
    )

    return render_template(
        "alumno/penalizaciones.html",
        penalizaciones=penalizaciones if isinstance(penalizaciones, list) else [],
        fetch_error=error,
    )

@alumno_bp.route("/mis-reservas")
def alumno_mis_reservas():
    """Vista de reservas activas y en curso del alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    mensaje_error = request.args.get("mensaje_error")
    usuario_id = usuario.get("id")
    payload, error = obtener_reservas_usuario(usuario_id, token=token)

    reservas_activas = []
    if not error and isinstance(payload, list):
        for reserva in payload:
            estado = reserva.get("estado_reserva", "")
            if estado not in ("pendiente", "aprobado", "entregado"):
                continue
            reservas_activas.append(
                {
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
            )

    return render_template(
        "alumno/mis-reservas.html",
        reservas_activas=reservas_activas,
        fetch_error=error,
        mensaje_error=mensaje_error,
    )


@alumno_bp.route("/reservas/<int:id>/cancelar", methods=["POST"])
def alumno_cancelar_reserva(id):
    """Cancela una reserva pendiente del alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    next_view = request.form.get("next_view")
    redirect_endpoints = {
        "dashboard": "alumno.dashboard",
        "mis_reservas": "alumno.alumno_mis_reservas",
    }
    redirect_endpoint = redirect_endpoints.get(
        next_view, "alumno.alumno_mis_reservas"
    )

    cancelada, error, status = reservas_servicio.establecer_estado_reserva(
        id, {"estado_reserva": "cancelado"}, token=token
    )
    if error or not cancelada:
        return redirect(
            url_for(
                redirect_endpoint,
                mensaje_error="No se pudo cancelar la reserva.",
            )
        )

    return redirect(url_for(redirect_endpoint))
