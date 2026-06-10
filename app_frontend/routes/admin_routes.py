"""Rutas del area de administracion."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios.api_client import get_json, obtener_detalle_reserva, post_json
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

    try:
        datos_api = obtener_detalle_reserva(id)
        reserva = {
            "id": datos_api.get("id", id),
            "estado_general": datos_api.get("estado_reserva", "pendiente"),
            "estado_texto": datos_api.get("estado_reserva", "Pendiente"),
            "estado_clase": "status-pending"
            if datos_api.get("estado_reserva") == "pendiente"
            else "status-active",
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
            "estado_clase": "status-error",
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

    articulos = articulos_servicio.obtener_articulos()

    return render_template(
        "admin/articulos.html",
        articulos=articulos,
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

    _, error, _ = post_json("/articulos", payload, token=token)

    if error:
        return redirect(url_for("admin.crear_articulo", error=error))

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

    """usuarios, error = get_json("/usuario", token=token)
    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios if isinstance(usuarios, list) else [],
        fetch_error=error,
    )"""

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
    usuarios = usuario_servicio.obtener_usuarios(params={"page": page}, token=token)    
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
    )

"""
@admin_bp.route("/usuarios/eliminar", methods=["POST"])
def eliminar_usuario():
    Elimina un usuario desde el rol administrador.

    token = session.get("token")
    rol = session.get("rol")

    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    id_usuario = request.form.get("id")
    eliminar_usuario(id_usuario)

    return redirect(url_for("admin.usuarios"))
"""

@admin_bp.route("/reportes/morosidad")
def reporte_morosidad():
    """Renderiza la vista de reporte de morosidad para administradores."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    penalizaciones, error = get_json("/penalizaciones", token=token)

    rows = []
    if isinstance(penalizaciones, list):
        for penalty in penalizaciones:
            rows.append(
                {
                    "usuario": penalty.get("id_usuario") or penalty.get("usuarioId"),
                    "articulo": penalty.get("id_reserva") or penalty.get("reservaId"),
                    "vencimiento": penalty.get("fecha_fin")
                    or penalty.get("resolvedAt"),
                    "estado": "Activa" if penalty.get("activa", True) else "Levantada",
                }
            )

    return render_template("admin/morosidad.html", penalizaciones=rows, fetch_error=error)


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

        _, error = post_json(
            f"/articulos/{id}/update", data=datos_actualizados, token=token
        )

        if error:
            return render_template("admin/editar_articulo.html", fetch_error=error)

        return redirect(url_for("admin.listar_articulos"))

    articulo, error = get_json(f"/articulos/{id}", token=token)

    return render_template(
        "admin/editar_articulo.html", articulo=articulo, fetch_error=error
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

    lista_filtros = []

    if estado:
        lista_filtros.append(f"estado={estado}")
    if usuario:
        lista_filtros.append(f"usuario={usuario}")
    if fecha:
        lista_filtros.append(f"fecha={fecha}")

    query_params = ""
    if lista_filtros:
        query_params = "?" + "&".join(lista_filtros)

    url_final = f"/reservas{query_params}"
    reservas, error = get_json(url_final, token=token)

    return render_template(
        "admin/reservas.html",
        reservas=reservas or [],
        fetch_error=error,
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

    penalizaciones, error = get_json("/penalizaciones", token=token)

    lista_penalizaciones = []

    if isinstance(penalizaciones, list):
        for p in penalizaciones:
            lista_penalizaciones.append(
                {
                    "id": p.get("id"),
                    "usuario_nombre": p.get("nombre_usuario", "Desconocido"),
                    "severidad": p.get("severidad", "Media"),
                    "fecha_inicio": p.get("fecha_inicio", "N/A"),
                    "activa": p.get("activa", True),
                }
            )

    return render_template(
        "admin/penalizaciones.html",
        penalizaciones=lista_penalizaciones,
        fetch_error=error,
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

    post_json(f"/penalizaciones/{id}/resolve", {}, token=token)
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

    payload = {
        "rol": request.form.get("rol"),
        "email": request.form.get("email"),
        "carrera": request.form.get("carrera"),
    }
    payload = {k: v for k, v in payload.items() if v is not None and v != ""}
    usuario_servicio.actualizar_usuario(id, payload, token=token)

    return redirect(url_for("admin.usuario_detalle", id=id))

@admin_bp.route("/usuarios/<int:id>/eliminar", methods=["POST"])
def eliminar_usuario(id):
    """Elimina un usuario del sistema."""
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    post_json(f"/usuarios/{id}", {}, token=token)
    return redirect(url_for("admin.usuarios"))