"""Rutas del area de administracion."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios.api_client import obtener_detalle_reserva
from servicios.fechas_servicio import formatear_fecha_argentina
from servicios.paginacion_servicio import paginar_lista, DEFAULT_PER_PAGE
from servicios.normativas_servicio import (
    actualizar_normativa,
    crear_normativa,
    eliminar_normativa,
    obtener_normativas,
)
from servicios.reports_servicio import obtener_reportes
from servicios.articulos_servicio import eliminar_articulo
from servicios import articulos_servicio
from servicios import usuario_servicio
from servicios import penalizaciones_servicio
from servicios import reservas_servicio

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/reservas/<int:id>", methods=["GET", "POST"])
def reserva_detalle(id):
    """Renderiza y procesa la vista de detalle de préstamo para administradores."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    if request.method == "POST":
        return redirect(url_for("admin.reserva_detalle", id=id))

    estado_clases = {
        "pendiente": "status-pending",
        "aprobado": "status-aprobado",
        "devuelto": "status-devuelto",
        "rechazado": "status-rechazado",
        "cancelado": "status-cancelado",
    }

    try:
        datos_api = obtener_detalle_reserva(id)
        estado = datos_api.get("estado_reserva", "pendiente")
        reserva = {
            "id": datos_api.get("id", id),
            "estado_general": estado,
            "estado_texto": estado,
            "estado_clase": estado_clases.get(estado, "status-pending"),
            "equipo_nombre": datos_api.get("nombre_art", "Material no especificado"),
            "equipo_id": datos_api.get("id_reservado", "N/A"),
            "titular_nombre": datos_api.get("nombre", "Alumno"),
            "titular_legajo": datos_api.get("id_usuario", "N/A"),
            "titular_carrera": datos_api.get("carrera", "No definida"),
            "fecha_retiro": datos_api.get("fecha_retiro", "N/A"),
            "fecha_limite": datos_api.get("fecha_regreso", "N/A"),
        }
    except Exception:
        reserva = {
            "id": id,
            "estado_general": "error",
            "estado_texto": "Error al cargar",
            "estado_clase": "status-pending",
            "equipo_nombre": "No disponible",
            "equipo_id": "N/A",
            "titular_nombre": "Usuario",
            "titular_legajo": "N/A",
            "titular_carrera": "N/A",
            "fecha_retiro": "N/A",
            "fecha_limite": "N/A",
        }

    return render_template("admin/reserva_detalle_admin.html", reserva=reserva)


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

    from servicios.paginacion_servicio import paginar_lista

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
    if not token:
        return redirect(url_for("public.login"))

    eliminar_articulo(id, token=token)
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

    rta = obtener_reportes("careers")

    carreras = rta.get("datos", [])

    return render_template("admin/reportes.html", carreras=carreras)


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
            actualizar_normativa(id_normativa, data)
        else:
            crear_normativa(data)
        return redirect(url_for("admin.normativas"))

    normativas = obtener_normativas()
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
    eliminar_normativa(id_norm)
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
            "carera": request.form.get("carrera"),
            "puntaje": request.form.get("puntaje"),
            "activo": request.form.get("activo"),
        }
        if id_usuario:
            usuario_servicio.actualizar_usuario(id_usuario, data, token=token)

        return redirect(url_for("admin.usuarios"))

    page = request.args.get("page", 1, type=int)
    nombre_usuario = request.args.get("usuario")
    usuarios = usuario_servicio.obtener_usuarios(params={"page": page, "usuario": nombre_usuario}, token=token)
    usuario_editado = None
    id_editar = request.args.get("editar")

    if id_editar:
        for usuario in usuarios:
            if str(usuario["id"]) == str(id_editar):
                usuario_editado = usuario
                break

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios,
        page=page,
        usuario_editado=usuario_editado,
        creando_usuario=request.args.get("creando_usuario") == "1",
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

    id = request.form.get("id")
    usuario_servicio.eliminar_usuario(id, token=token)

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
    page = request.args.get("page", 1, type=int)
    params = {"usuario": usuario} if usuario else {}

    penalizaciones_raw = penalizaciones_servicio.obtener_penalizaciones(
        params=params or None, token=token
    )

    penalizaciones_formateadas = []
    if isinstance(penalizaciones_raw, list):
        for p in penalizaciones_raw:
            penalizaciones_formateadas.append({
                **p,
                "fecha_fin": formatear_fecha_argentina(p.get("fecha_fin")),
            })

    penalizaciones, pagination = paginar_lista(penalizaciones_formateadas, pagina=page)

    return render_template(
        "admin/morosidad.html",
        penalizaciones=penalizaciones,
        usuario=usuario or "",
        fetch_error=None,
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
            articulo = articulos_servicio.obtener_articulo(id, token=token)
            return render_template(
                "admin/editar_articulo.html",
                articulo=articulo,
                fetch_error="No se pudo actualizar el artículo. Intentá de nuevo.",
            )

        return redirect(url_for("admin.listar_articulos"))

    articulo = articulos_servicio.obtener_articulo(id, token=token)

    return render_template(
        "admin/editar_articulo.html",
        articulo=articulo,
        fetch_error=None,
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

    raw = reservas_servicio.obtener_reservas(params=params or None)

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

    penalizaciones = penalizaciones_servicio.obtener_penalizaciones(token=token)

    lista_penalizaciones = []

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

    page = request.args.get("page", 1, type=int)
    lista_penalizaciones, pagination = paginar_lista(lista_penalizaciones, pagina=page)

    return render_template(
        "admin/penalizaciones.html",
        penalizaciones=lista_penalizaciones,
        pagination=pagination,
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

    penalizaciones_servicio.actualizar_parcial_penalizacion(id, {"status": "Levantada"}, token=token)
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
    return render_template("admin/perfil_usuario.html", usuario=usuario)


@admin_bp.route("/usuarios/<int:id>/editar", methods=["POST"])
def editar_usuario(id):
    """Actualiza el rol de un usuario y redirige a su perfil."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))
    if rol != "bibliotecario":
        return redirect(url_for("admin.usuario_detalle", id=id))

    payload = {
        "rol": request.form.get("rol"),
        "email": request.form.get("email"),
        "carrera": request.form.get("carrera"),
    }
    payload = {k: v for k, v in payload.items() if v is not None and v != ""}
    usuario_servicio.actualizar_usuario(id, payload, token=token)

    return redirect(url_for("admin.usuario_detalle", id=id))