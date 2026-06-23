"""Rutas del area de administracion."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios.fechas_servicio import formatear_fecha_argentina
from servicios.paginacion_servicio import (
    DEFAULT_API_LIMIT,
    adaptar_pagination_hateoas,
    calcular_offset,
    paginar_lista,
)
from servicios.normativas_servicio import (
    actualizar_normativa,
    crear_normativa,
    eliminar_normativa,
    obtener_normativas,
)
from servicios.reports_servicio import obtener_reportes
from servicios import articulos_servicio
from servicios import usuario_servicio
from servicios import penalizaciones_servicio
from servicios import reservas_servicio

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/reservas/<int:reserva_id>", methods=["GET", "POST"])
def reserva_detalle(reserva_id):
    """Renderiza y procesa la vista de detalle de préstamo para administradores."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    if request.method == "POST":
        mensaje_error_estado = "No se pudo cambiar el estado de la reserva."
        estado_reserva = request.form.get("estado_reserva")
        if not estado_reserva:
            return redirect(
                url_for(
                    "admin.reserva_detalle",
                    reserva_id=reserva_id,
                    mensaje_error=mensaje_error_estado,
                )
            )

        status_data = {"estado_reserva": estado_reserva}
        estado_devuelto = request.form.get("estado_devuelto")
        if estado_devuelto:
            status_data["estado_devuelto"] = estado_devuelto

        actualizada, error, status = reservas_servicio.establecer_estado_reserva(
            reserva_id, status_data, token=token
        )
        if error or not actualizada:
            return redirect(
                url_for(
                    "admin.reserva_detalle",
                    reserva_id=reserva_id,
                    mensaje_error=error or mensaje_error_estado,
                )
            )
        return redirect(url_for("admin.reserva_detalle", reserva_id=reserva_id))

    estado_clases = {
        "pendiente": "status-pendiente",
        "aprobado": "status-aprobado",
        "entregado": "status-entregado",
        "devuelto": "status-devuelto",
        "rechazado": "status-rechazado",
        "cancelado": "status-cancelado",
    }

    try:
        datos_api = reservas_servicio.obtener_detalle_reserva(reserva_id, token=token)
        estado = datos_api.get("estado_reserva", "pendiente")
        reserva = {
            "id": datos_api.get("id", reserva_id),
            "estado_general": estado,
            "estado_texto": estado,
            "estado_clase": estado_clases.get(estado, "status-pendiente"),
            "equipo_nombre": datos_api.get("nombre_art", "Material no especificado"),
            "equipo_id": datos_api.get("id_reservado", "N/A"),
            "titular_nombre": datos_api.get("nombre", "Alumno"),
            "titular_legajo": datos_api.get("id_usuario", "N/A"),
            "titular_carrera": datos_api.get("carrera", "No definida"),
            "fecha_retiro": formatear_fecha_argentina(datos_api.get("fecha_retiro")),
            "fecha_limite": formatear_fecha_argentina(datos_api.get("fecha_regreso")),
            "estado_devuelto": datos_api.get("estado_devuelto") or "no_aplica",
            "dias_retraso": datos_api.get("dias_retraso"),
            "condiciones": datos_api.get("condiciones"),
        }
    except Exception:
        reserva = {
            "id": reserva_id,
            "estado_general": "error",
            "estado_texto": "Error al cargar",
            "estado_clase": "status-pendiente",
            "equipo_nombre": "No disponible",
            "equipo_id": "N/A",
            "titular_nombre": "Usuario",
            "titular_legajo": "N/A",
            "titular_carrera": "N/A",
            "fecha_retiro": "N/A",
            "fecha_limite": "N/A",
            "estado_devuelto": "no_aplica",
            "dias_retraso": None,
            "condiciones": None,
        }

    return render_template(
        "admin/reserva_detalle_admin.html",
        reserva=reserva,
        mensaje_error=request.args.get("mensaje_error"),
    )


@admin_bp.route("/articulos")
def listar_articulos():
    """Renderiza la vista de listado de artículos para administradores."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    filtro_tipo = request.args.get("tipo", "").strip().lower()
    filtro_seccion = request.args.get("seccion", "").strip().lower()
    filtro_nombre = request.args.get("nombre", "").strip().lower()
    pagina = request.args.get("page", 1, type=int)

    todos = articulos_servicio.obtener_articulos(token=token)

    tipos = sorted({(a.get("tipo") or "").strip() for a in todos if a.get("tipo")})
    secciones = sorted({(a.get("seccion") or "").strip() for a in todos if a.get("seccion")})

    filtrados = todos
    if filtro_tipo:
        filtrados = [a for a in filtrados if filtro_tipo in (a.get("tipo") or "").lower()]
    if filtro_seccion:
        filtrados = [a for a in filtrados if filtro_seccion in (a.get("seccion") or "").lower()]
    if filtro_nombre:
        filtrados = [a for a in filtrados if filtro_nombre in (a.get("nombre_art") or "").lower()]

    articulos_pagina, pagination = paginar_lista(filtrados, pagina=pagina, por_pagina=10)

    return render_template(
        "admin/articulos.html",
        articulos=articulos_pagina,
        pagination=pagination,
        tipos=tipos,
        secciones=secciones,
        filtro_tipo=filtro_tipo,
        filtro_seccion=filtro_seccion,
        filtro_nombre=filtro_nombre,
        mensaje_error=request.args.get("mensaje_error"),
    )


@admin_bp.route("/articulos/nuevo")
def crear_articulo():
    """Renderiza la vista de creación de nuevo artículo para administradores."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    return render_template(
        "admin/articulos_form.html",
        articulo=None,
        form_error=request.args.get("error"),
        form_exito=request.args.get("exito"),
    )


@admin_bp.route("/articulos/guardar", methods=["POST"])
def guardar_articulo():
    """Crea un artículo consumiendo el endpoint backend /api/articulos."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    payload = {
        "nombre_art": request.form.get("nombre"),
        "tipo": request.form.get("tipo"),
        "seccion": request.form.get("seccion"),
        "prestacion_maxima": 7,
        "stock": int(request.form.get("stock") or 1),
        "necesita_reparacion": False,
    }

    resultado = articulos_servicio.crear_articulo(payload, token=token)

    if not resultado:
        return redirect(url_for("admin.crear_articulo", error="No se pudo crear el artículo"))

    return redirect(
        url_for("admin.crear_articulo", exito="Artículo creado correctamente")
    )


@admin_bp.route("/articulos/<int:id>/eliminar", methods=["POST"])
def eliminar_articulo_route(id):
    """Elimina un articulo."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    eliminado, error, status = articulos_servicio.eliminar_articulo(id, token=token)
    if error or not eliminado:
        return redirect(
            url_for(
                "admin.listar_articulos",
                mensaje_error=error or "No se pudo eliminar el artículo.",
            )
        )

    return redirect(url_for("admin.listar_articulos"))


@admin_bp.route("/dashboard")
def dashboard():
    """Renderiza la vista del dashboard para administradores."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    return render_template("admin/dashboard.html")


@admin_bp.route("/reportes", methods=["GET"])
def reportes():
    """Renderiza la vista de reportes para administradores."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    rta_carreras = obtener_reportes("carreras", token=token)
    carreras = rta_carreras.get("datos", [])

    rta_articulos = obtener_reportes("articulos", token=token)
    articulos = rta_articulos.get("datos", [])

    return render_template("admin/reportes.html", carreras=carreras, articulos=articulos)


@admin_bp.route("/normativas", methods=["GET", "POST"])
def normativas():
    """ABM de normativas solo visibles para admins y bibliotecarios."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    if request.method == "POST":
        id_normativa = request.form.get("id")
        data = {
            "titulo": request.form.get("titulo"),
            "descripcion": request.form.get("descripcion"),
        }
        if id_normativa:
            payload, error, status = actualizar_normativa(id_normativa, data, token=token)
            if error:
                return redirect(
                    url_for(
                        "admin.normativas",
                        mensaje_error="No se pudo actualizar la normativa.",
                    )
                )
        else:
            payload, error, status = crear_normativa(data, token=token)
            if error:
                return redirect(
                    url_for(
                        "admin.normativas",
                        mensaje_error="No se pudo crear la normativa.",
                    )
                )
        return redirect(url_for("admin.normativas"))

    normativas = [
        {
            **normativa,
            "fecha": formatear_fecha_argentina(normativa.get("fecha")),
        }
        for normativa in obtener_normativas()
    ]
    normativa_editada = None
    id_editar = request.args.get("editar")

    if id_editar:
        for normativa in normativas:
            if str(normativa["id"]) == str(id_editar):
                normativa_editada = normativa
                break

    return render_template(
        "admin/normativas.html",
        normativas=normativas,
        normativa_editada=normativa_editada,
        mensaje_error=request.args.get("mensaje_error"),
    )


@admin_bp.route("/normativas/eliminar", methods=["POST"])
def eliminar_norm():
    """Descripción: función eliminar_norm."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    id_norm = request.form.get("id")
    eliminada, error, status = eliminar_normativa(id_norm, token=token)
    if error or not eliminada:
        return redirect(
            url_for(
                "admin.normativas",
                mensaje_error="No se pudo eliminar la normativa.",
            )
        )
    return redirect(url_for("admin.normativas"))


@admin_bp.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    """ABM de usuarios para administradores."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    if request.method == "POST":
        id_usuario = request.form.get("id")
        data = {
            "nombre": request.form.get("nombre"),
            "email": request.form.get("email"),
            "carrera": request.form.get("carrera"),
        }
        if id_usuario:
            data["activo"] = request.form.get("activo") == "1"
            payload, error, status = usuario_servicio.actualizar_usuario(
                id_usuario, data, token=token
            )
            if error:
                return redirect(
                    url_for(
                        "admin.usuarios",
                        mensaje_error="No se pudo actualizar el usuario.",
                    )
                )
        else:
            data["contrasenia"] = request.form.get("contrasenia")
            payload, error, status = usuario_servicio.crear_usuario(data, token=token)
            if error:
                return redirect(
                    url_for(
                        "admin.usuarios",
                        creando_usuario=1,
                        mensaje_error="No se pudo crear el usuario.",
                    )
                )

        return redirect(url_for("admin.usuarios"))

    pagina = request.args.get("page", 1, type=int)
    nombre_usuario = request.args.get("usuario")
    offset = calcular_offset(pagina, DEFAULT_API_LIMIT)
    filtros = {"limit": DEFAULT_API_LIMIT, "offset": offset}
    if nombre_usuario:
        filtros["usuario"] = nombre_usuario

    payload_paginado, fetch_error = usuario_servicio.obtener_usuarios_paginados(
        params=filtros,
        token=token,
    )
    usuarios_paginados = payload_paginado.get("data", [])
    pagination = adaptar_pagination_hateoas(payload_paginado, pagina=pagina)
    usuario_editado = None
    id_editar = request.args.get("editar")

    if id_editar:
        for usuario in usuarios_paginados:
            if str(usuario.get("id")) == str(id_editar):
                usuario_editado = usuario
                break

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios_paginados,
        pagination=pagination,
        usuario=nombre_usuario or "",
        usuario_editado=usuario_editado,
        creando_usuario=request.args.get("creando_usuario") == "1",
        mensaje_error=request.args.get("mensaje_error") or fetch_error,
    )


@admin_bp.route("/usuarios/eliminar", methods=["POST"])
def eliminar_usuario():
    """Elimina un usuario del sistema."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    id_usuario = request.form.get("id") or request.args.get("id")
    eliminado, error, status = usuario_servicio.eliminar_usuario(id_usuario, token=token)
    if error or not eliminado:
        return redirect(
            url_for(
                "admin.usuarios",
                mensaje_error="No se pudo eliminar el usuario.",
            )
        )

    return redirect(url_for("admin.usuarios"))


@admin_bp.route("/reportes/morosidad")
def reporte_morosidad():
    """Reporte de morosidad."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    usuario = request.args.get("usuario")
    pagina = request.args.get("page", 1, type=int)
    offset = calcular_offset(pagina, DEFAULT_API_LIMIT)
    filtros = {"limit": DEFAULT_API_LIMIT, "offset": offset}
    if usuario:
        filtros["usuario"] = usuario

    payload_paginado, fetch_error = penalizaciones_servicio.obtener_penalizaciones_paginadas(
        params=filtros,
        token=token,
    )

    penalizaciones_formateadas = []
    penalizaciones_raw = payload_paginado.get("data", [])
    if isinstance(penalizaciones_raw, list):
        for p in penalizaciones_raw:
            penalizaciones_formateadas.append({
                **p,
                "fecha_fin": formatear_fecha_argentina(p.get("fecha_fin")),
            })

    pagination = adaptar_pagination_hateoas(payload_paginado, pagina=pagina)

    return render_template(
        "admin/morosidad.html",
        penalizaciones=penalizaciones_formateadas,
        usuario=usuario or "",
        fetch_error=fetch_error,
        pagination=pagination,
    )


@admin_bp.route("/articulos/<int:id>/editar", methods=["GET", "POST"])
def editar_articulo(id):
    """Formulario de edición de artículo: muestra datos y permite actualizarlos."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    if request.method == "POST":
        raw_stock = request.form.get("stock", "0")
        stock = int(raw_stock) if raw_stock.isdigit() else 0

        datos_actualizados = {
            "nombre_art": request.form.get("nombre"),
            "tipo": request.form.get("tipo"),
            "seccion": request.form.get("seccion"),
            "stock": stock,
            "necesita_reparacion": request.form.get("necesita_reparacion") == "on",
        }

        resultado = articulos_servicio.actualizar_articulo(id, datos_actualizados, token=token)

        if not resultado:
            articulo, fetch_error = articulos_servicio.obtener_articulo(id, token=token)
            return render_template(
                "admin/editar_articulo.html",
                articulo=articulo,
                fetch_error=fetch_error or "No se pudo actualizar el artículo. Intentá de nuevo.",
            )

        return redirect(url_for("admin.listar_articulos"))

    articulo, fetch_error = articulos_servicio.obtener_articulo(id, token=token)

    return render_template(
        "admin/editar_articulo.html",
        articulo=articulo,
        fetch_error=fetch_error,
    )


@admin_bp.route("/reservas", methods=["GET"])
def lista_reservas():
    """Lista todos los préstamos con filtros por estado, fecha o usuario."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    estado = request.args.get("estado")
    usuario = request.args.get("usuario")
    fecha = request.args.get("fecha")
    page = request.args.get("page", 1, type=int)

    params = {}
    if estado:
        params["estado"] = estado
    if usuario:
        params["usuario"] = usuario
    if fecha:
        params["fecha"] = fecha

    raw = reservas_servicio.obtener_reservas(params=params or None, token=token)

    reservas = [
        {
            "id": r.get("id"),
            "usuario_nombre": r.get("usuario_nombre", f"Usuario #{r.get('id_usuario')}"),
            "nombre_art": r.get("nombre_art", "—"),
            "estado_reserva": r.get("estado_reserva", "—"),
            "fecha": formatear_fecha_argentina(r.get("fecha_retiro")),
        }
        for r in raw
    ]

    reservas_paginadas, pagination = paginar_lista(reservas, pagina=page)

    return render_template(
        "admin/reservas.html",
        reservas=reservas_paginadas,
        pagination=pagination,
    )


@admin_bp.route("/penalizaciones", methods=["GET"])
def listar_penalizaciones():
    """Lista las penalizaciones activas."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    pagina = request.args.get("page", 1, type=int)
    offset = calcular_offset(pagina, DEFAULT_API_LIMIT)
    filtros = {"limit": DEFAULT_API_LIMIT, "offset": offset}
    payload_paginado, fetch_error = penalizaciones_servicio.obtener_penalizaciones_paginadas(
        params=filtros,
        token=token,
    )

    lista_penalizaciones = []
    penalizaciones = payload_paginado.get("data", [])

    if isinstance(penalizaciones, list):
        for p in penalizaciones:
            lista_penalizaciones.append(
                {
                    "id": p.get("id"),
                    "usuario_nombre": p.get("nombre", "Desconocido"),
                    "severidad": p.get("severidad", "Media"),
                    "fecha_inicio": formatear_fecha_argentina(p.get("fecha_inicio")),
                    "activa": p.get("activa", True),
                }
            )

    pagination = adaptar_pagination_hateoas(payload_paginado, pagina=pagina)

    return render_template(
        "admin/penalizaciones.html",
        penalizaciones=lista_penalizaciones,
        pagination=pagination,
        mensaje_error=request.args.get("mensaje_error"),
        fetch_error=fetch_error,
    )


@admin_bp.route("/penalizaciones/nueva", methods=["GET", "POST"])
def crear_penalizacion():
    """Formulario de alta de penalización (solo bibliotecario)."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    if rol != "bibliotecario":
        return redirect(url_for("admin.listar_penalizaciones"))

    if request.method == "POST":
        usuario_id = request.form.get("usuario_id")
        motivo = request.form.get("reason")

        if not usuario_id or not motivo:
            usuarios = usuario_servicio.obtener_usuarios(token=token)
            return render_template(
                "admin/penalizaciones_form.html",
                usuarios=usuarios,
                form_error="Usuario y motivo son obligatorios.",
            )

        resultado = penalizaciones_servicio.crear_penalizacion(
            {"usuario_id": usuario_id, "reason": motivo, "severidad": request.form.get("severidad", "media")},
            token=token,
        )

        if not resultado:
            usuarios = usuario_servicio.obtener_usuarios(token=token)
            return render_template(
                "admin/penalizaciones_form.html",
                usuarios=usuarios,
                form_error="No se pudo crear la penalización.",
            )

        return redirect(url_for("admin.listar_penalizaciones"))

    usuarios = usuario_servicio.obtener_usuarios(token=token)

    return render_template(
        "admin/penalizaciones_form.html",
        usuarios=usuarios,
        form_error=None,
    )


@admin_bp.route("/penalizaciones/<int:id>/levantar", methods=["POST"])
def levantar_penalizacion(id):
    """Acción para levantar una penalización manualmente."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    if rol != "bibliotecario":
        return redirect(url_for("admin.listar_penalizaciones"))

    actualizada, error, status = penalizaciones_servicio.actualizar_parcial_penalizacion(
        id, {"status": "Levantada"}, token=token
    )
    if error or not actualizada:
        return redirect(
            url_for(
                "admin.listar_penalizaciones",
                mensaje_error="No se pudo levantar la penalización.",
            )
        )
    return redirect(url_for("admin.listar_penalizaciones"))


@admin_bp.route("/usuarios/<int:id>", methods=["GET"])
def usuario_detalle(id):
    """Renderiza el perfil completo de un usuario para administradores."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    usuario = usuario_servicio.obtener_usuario(id, token=token)
    return render_template(
        "admin/perfil_usuario.html",
        usuario=usuario,
        mensaje_error=request.args.get("mensaje_error"),
    )


@admin_bp.route("/usuarios/<int:id>/editar", methods=["POST"])
def editar_usuario(id):
    """Actualiza el rol de un usuario y redirige a su perfil."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    payload = {
        "rol": request.form.get("rol"),
        "email": request.form.get("email"),
        "carrera": request.form.get("carrera"),
    }
    payload = {k: v for k, v in payload.items() if v is not None and v != ""}
    usuario_actualizado, error, status = usuario_servicio.actualizar_usuario(
        id, payload, token=token
    )
    if error:
        return redirect(
            url_for(
                "admin.usuario_detalle",
                id=id,
                mensaje_error="No se pudo actualizar el usuario.",
            )
        )

    return redirect(url_for("admin.usuario_detalle", id=id))
