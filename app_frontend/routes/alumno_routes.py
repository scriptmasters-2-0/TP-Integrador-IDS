"""Rutas del area de alumnos."""

import logging

from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios.api_client import (
    get_json,
    obtener_detalle_reserva,
    obtener_perfil_usuario,
    post_json,
)
from servicios.fechas_servicio import formatear_fecha_argentina
from servicios.historial_filtros_servicio import (
    estados_disponibles,
    filtrar_historial_reservas,
)
from servicios.paginacion_servicio import DEFAULT_PER_PAGE, paginar_lista
from servicios.usuario_servicio import (
    obtener_penalizaciones_usuario,
    obtener_reservas_usuario_con_error,
)

logger = logging.getLogger(__name__)
alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")


@alumno_bp.route("/perfil")
def perfil():
    """Renderiza la página de perfil del alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    mensaje = request.args.get("mensaje")
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    try:
        from servicios.auth_servicio import obtener_mi_perfil
        perfil_fresco = obtener_mi_perfil(token=token)
        if perfil_fresco and "usuario" in perfil_fresco:
            usuario = perfil_fresco["usuario"]
    except Exception as e:
        logger.error(f"Error fetching usuario profile: {e}")

    return render_template("alumno/perfil.html", usuario=usuario, mensaje=mensaje)

@alumno_bp.route("/cambiar_contrasena", methods=["POST"])
def cambiar_contrasena():
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))
        
    nueva_contrasena = request.form.get("nueva_contrasena")
    usuario_id = usuario.get("id")
    
    from servicios.usuario_servicio import actualizar_usuario
    # Se actualiza enviando el campo contrasenia
    actualizar_usuario(usuario_id, {"contrasenia": nueva_contrasena}, token=token)
    
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
    payload, error = obtener_reservas_usuario_con_error(usuario_id, token=token)
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
                    "estado_clase": (
                        "badge-warning"
                        if estado_reserva == "pendiente"
                        else "badge-success"
                    ),
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
        if usuario_id and articulo_id:
            post_json(
                "/reservas",
                {"usuario_id": usuario_id, "articulo_id": articulo_id},
                token=token,
            )
        return redirect(url_for("alumno.historial"))

    articulos_payload, fetch_error = get_json("/articulos", token=token)
    articulos = articulos_payload if isinstance(articulos_payload, list) else []

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
        datos_api = obtener_detalle_reserva(id)
        
        reserva = {
            "id": datos_api.get("id", id),
            "estado_texto": datos_api.get("estado_reserva", "pendiente"),
            "estado_clase": "status-active",
            "equipo_nombre": datos_api.get("nombre_art", "Material no especificado"),
            "equipo_id": datos_api.get("id_reservado", "N/A"),
            "sede": datos_api.get("seccion", "Sede Central FIUBA"),
            "fecha_reserva": formatear_fecha_argentina(datos_api.get("fecha_retiro")),
            "fecha_retiro": formatear_fecha_argentina(datos_api.get("fecha_retiro")),
            "fecha_limite": formatear_fecha_argentina(datos_api.get("fecha_regreso")),
            "titular_nombre": datos_api.get("nombre", "Alumno"),
            "titular_legajo": datos_api.get("id_usuario", "N/A"),
        }
    except Exception as e:
        logger.error(f"Error retrieving reserva detail for ID {id}: {e}")
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

    return render_template("alumno/comprobante.html", reserva=reserva)


@alumno_bp.route("/reservas/id/comprobante")
def comprobante_sin_id():
    """Redirige comprobantes sin reserva al historial."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    return redirect(url_for("alumno.historial"))


# TODO: Implement POST handlers for profile management
# These handlers are placeholders for features to be implemented:
# - @alumno_bp.route("/perfil/cambiar-contrasena", methods=["POST"]) - Change contrasenia
# - @alumno_bp.route("/perfil/solicitar-correccion", methods=["POST"]) - Request data correction
# Currently, these buttons are disabled in the template (alumno/perfil.html)
# Backend endpoints in /api/usuarios/*/contrasenia and /api/usuarios/*/corrections should be created


@alumno_bp.route("/dashboard")
def dashboard():
    """Panel principal: reservas activas, puntaje, alertas de penalización."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    dashboard_data, error = get_json(
        f"/alumno/dashboard/{usuario.get('id')}", token=token
    )

    return render_template(
        "alumno/dashboard.html", dashboard=dashboard_data or {}, fetch_error=error
    )


@alumno_bp.route("/reservas/<int:id>", methods=["GET"])
def reserva_detalle(id):
    """Detalle de reserva: estado, fecha retiro/regreso, QR."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    datos_api, error = get_json(f"/reservas/{id}", token=token)

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
        
    reserva = {
        "id": datos_api.get("id"),
        "estado": datos_api.get("estado_reserva"),
        "fecha_retiro": formatear_fecha_argentina(datos_api.get("fecha_retiro")),
        "fecha_regreso": formatear_fecha_argentina(datos_api.get("fecha_regreso")),
        "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=FIUBA-RES-{datos_api.get('id')}",
    }

    return render_template("alumno/reserva_detalle_alumno.html", reserva=reserva)

@alumno_bp.route("/penalizaciones")
def alumno_penalizaciones():
    """Renderiza las penalizaciones activas del alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    usuario_id = usuario.get("id")
    penalizaciones, error = get_json(f"/penalizaciones?usuario_id={usuario_id}", token=token)

    return render_template(
        "alumno/penalizaciones.html",
        penalizaciones=penalizaciones if isinstance(penalizaciones, list) else [],
        fetch_error=error,
    )

@alumno_bp.route("/reservas/<int:id>/cancelar", methods=["POST"])
def cancelar_reserva(id):
    """Cancela una reserva pendiente del alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))
    post_json(f"/reservas/{id}/cancelar", {}, token=token)
    return redirect(url_for("alumno.historial"))

@alumno_bp.route("/mis-reservas")
def alumno_mis_reservas():
    """Alias para mis reservas del alumno."""
    token = session.get("token")
    usuario = session.get("usuario")
    if not token or not usuario:
        return redirect(url_for("public.login"))

    usuario_id = usuario.get("id")
    reservas, error = get_json(f"/usuarios/{usuario_id}/reservas", token=token)

    return render_template(
        "alumno/mis-reservas.html",
        reservas=reservas if isinstance(reservas, list) else [],
        fetch_error=error,
    )


@alumno_bp.route("/reservas/<int:id>/cancelar", methods=["POST"])
def alumno_cancelar_reserva(id):
    """Alias para cancelar reserva del alumno."""
    return cancelar_reserva(id)
