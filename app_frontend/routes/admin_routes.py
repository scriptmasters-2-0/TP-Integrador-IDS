"""Rutas del área de administración del frontend.

Define las vistas y acciones disponibles para administradores y
bibliotecarios: gestión de usuarios, penalizaciones, artículos,
reservas, reportes y normativas.
"""

from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios.fechas_servicio import formatear_fecha_argentina
from servicios.paginacion_servicio import (
    paginar_lista,
    calcular_offset,
    extraer_data_paginada,
    adaptar_pagination_hateoas,
    DEFAULT_API_LIMIT
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


@admin_bp.route("/reservas/<int:id>", methods=["GET", "POST"])
def reserva_detalle(id):
    """Renderiza y procesa la vista de detalle de un préstamo.

    En GET muestra los datos del préstamo obtenidos desde la API.
    En POST redirige al mismo endpoint (acción futura).
    Accesible solo para admin y bibliotecario.

    Args:
        id (int): Identificador del préstamo a visualizar.

    Returns:
        Response: Renderizado de admin/reserva_detalle_admin.html con
            los datos del préstamo, o redirección al login si no hay sesión.

    """
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
        datos_api = reservas_servicio.obtener_detalle_reserva(id, token=token)
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
    """Renderiza la vista de listado de artículos para administradores.

    Obtiene todos los artículos desde la API y aplica filtros opcionales
    por tipo, sección y nombre en el frontend. La paginación se realiza
    localmente sobre los resultados filtrados.

    Query params:
        tipo (str): Filtra artículos por tipo.
        seccion (str): Filtra artículos por sección.
        nombre (str): Filtra artículos por nombre (búsqueda parcial).
        page (int): Número de página a mostrar. Por defecto 1.

    Returns:
        Response: Renderizado de admin/articulos.html con los artículos
            paginados y los filtros activos.

    """
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
    """Renderiza el formulario de creación de un nuevo artículo.

    Accesible solo para admin y bibliotecario.

    Query params:
        error (str): Mensaje de error a mostrar si la creación falló.
        exito (str): Mensaje de éxito a mostrar si la creación fue exitosa.

    Returns:
        Response: Renderizado de admin/articulos_form.html con el
            formulario vacío y mensajes de estado opcionales.

    """
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
    """Procesa el formulario de creación de un artículo.

    Envía los datos del formulario a la API backend mediante POST
    /api/articulos. Redirige al formulario con mensaje de éxito o error
    según el resultado.

    Returns:
        Response: Redirección a admin.crear_articulo con query param
            'exito' o 'error' según el resultado de la operación.

    """
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
    """Elimina un artículo y redirige al listado.

    Envía DELETE /api/articulos/{id} a través del servicio de artículos.
    Accesible solo para usuarios con sesión activa.

    Args:
        id (int): Identificador del artículo a eliminar.

    Returns:
        Response: Redirección a admin.listar_articulos tras la operación.

    """
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
    """Renderiza el dashboard principal del área de administración.

    Accesible solo para admin y bibliotecario.

    Returns:
        Response: Renderizado de admin/dashboard.html.

    """
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    return render_template("admin/dashboard.html")


@admin_bp.route("/reportes", methods=["GET"])
def reportes():
    """Renderiza la vista de reportes estadísticos para administradores.

    Obtiene los reportes de reservas agrupadas por carrera y por artículo
    desde la API backend.

    Returns:
        Response: Renderizado de admin/reportes.html con las listas
            de datos por carrera y por artículo.

    """
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
    """ABM de normativas para administradores y bibliotecarios.

    En GET muestra el listado de normativas y, si se indica el parámetro
    'editar', preselecciona la normativa correspondiente en el formulario.
    En POST crea una nueva normativa o actualiza una existente según
    si se incluye el campo 'id' en el formulario.

    Query params (GET):
        editar (str): ID de la normativa a editar.

    Form params (POST):
        id (str): ID de la normativa a actualizar. Si está vacío, se crea una nueva.
        titulo (str): Título de la normativa.
        descripcion (str): Descripción de la normativa.

    Returns:
        Response: Renderizado de admin/normativas.html con el listado
            y la normativa preseleccionada para edición, o redirección
            tras el POST.

    """
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
        i = 0
        encontrado = False
        while i < len(normativas) and not encontrado:
            if str(normativas[i]["id"]) == str(id_editar):
                normativa_editada = normativas[i]
                encontrado = True
            i += 1

    return render_template(
        "admin/normativas.html",
        normativas=normativas,
        normativa_editada=normativa_editada,
        mensaje_error=request.args.get("mensaje_error"),
    )


@admin_bp.route("/normativas/eliminar", methods=["POST"])
def eliminar_norm():
    """Elimina una normativa y redirige al listado.

    Envía la solicitud de eliminación a la API backend mediante el
    servicio de normativas. Accesible solo para admin y bibliotecario.

    Form params:
        id (str): Identificador de la normativa a eliminar.

    Returns:
        Response: Redirección a admin.normativas tras la operación.

    """
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
    """ABM de usuarios para administradores y bibliotecarios.

    En GET muestra el listado paginado de usuarios con paginación HATEOAS.
    Si se indica el parámetro 'editar', preselecciona el usuario en el
    formulario. En POST actualiza los datos del usuario indicado por 'id'.

    Query params (GET):
        page (int): Número de página. Por defecto 1.
        usuario (str): Filtra usuarios por nombre (búsqueda parcial).
        editar (str): ID del usuario a preseleccionar en el formulario.
        creando_usuario (str): Si es '1', muestra el formulario de creación.

    Form params (POST):
        id (str): Identificador del usuario a actualizar.
        nombre (str): Nuevo nombre del usuario.
        email (str): Nuevo email del usuario.
        carrera (str): Nueva carrera del usuario.
        puntaje (str): Nuevo puntaje del usuario.
        activo (str): Estado activo del usuario.

    Returns:
        Response: Renderizado de admin/usuarios.html con el listado
            paginado y el usuario preseleccionado para edición,
            o redirección tras el POST.

    """
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

    page = request.args.get("page", 1, type=int)
    offset = calcular_offset(page, DEFAULT_API_LIMIT)
    nombre_usuario = request.args.get("usuario")

    resultado = usuario_servicio.obtener_usuarios_paginados(
        params={"limit": DEFAULT_API_LIMIT, "offset": offset, "usuario": nombre_usuario},
        token=token
    )
    usuarios = resultado.get("datos", [])
    pagination = adaptar_pagination_hateoas(resultado)

    usuario_editado = None
    id_editar = request.args.get("editar")

    if id_editar:
        i = 0
        encontrado = False
        while i < len(usuarios) and not encontrado:
            if str(usuarios[i]["id"]) == str(id_editar):
                usuario_editado = usuarios[i]
                encontrado = True
            i += 1

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios,
        pagination=pagination,
        usuario_editado=usuario_editado,
        creando_usuario=request.args.get("creando_usuario") == "1",
        mensaje_error=request.args.get("mensaje_error") or fetch_error,
    )


@admin_bp.route("/usuarios/eliminar", methods=["POST"])
def eliminar_usuario():
    """Da de baja lógica a un usuario y redirige al listado.

    Envía DELETE /api/usuarios/{id} a través del servicio de usuarios.
    Accesible solo para admin y bibliotecario.

    Form params:
        id (str): Identificador del usuario a dar de baja.

    Returns:
        Response: Redirección a admin.usuarios tras la operación.

    """
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
    """Renderiza el reporte de morosidad con paginación HATEOAS.

    Muestra las penalizaciones del sistema filtradas opcionalmente por
    nombre de usuario. Accesible solo para admin y bibliotecario.

    Query params:
        page (int): Número de página. Por defecto 1.
        usuario (str): Filtra penalizaciones por nombre de usuario.

    Returns:
        Response: Renderizado de admin/morosidad.html con el listado
            paginado de penalizaciones y el filtro activo.

    """
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    nombre_usuario = request.args.get("usuario")
    page = request.args.get("page", 1, type=int)
    offset = calcular_offset(page, DEFAULT_API_LIMIT)

    resultado = penalizaciones_servicio.obtener_penalizaciones_paginadas(
        params={"limit": DEFAULT_API_LIMIT, "offset": offset, "usuario": nombre_usuario},
        token=token
    )
    penalizaciones = resultado.get("datos", [])
    pagination = adaptar_pagination_hateoas(resultado)

    return render_template(
        "admin/morosidad.html",
        penalizaciones=penalizaciones,
        pagination=pagination,
        usuario=nombre_usuario or ""
    )


@admin_bp.route("/articulos/<int:id>/editar", methods=["GET", "POST"])
def editar_articulo(id):
    """Renderiza y procesa el formulario de edición de un artículo.

    En GET muestra el formulario con los datos actuales del artículo.
    En POST envía los datos actualizados a la API y redirige al listado
    si fue exitoso, o vuelve al formulario con un mensaje de error.

    Args:
        id (int): Identificador del artículo a editar.

    Form params (POST):
        nombre (str): Nuevo nombre del artículo.
        tipo (str): Nuevo tipo del artículo.
        seccion (str): Nueva sección del artículo.
        stock (str): Nuevo stock disponible.
        necesita_reparacion (str): 'on' si necesita reparación.

    Returns:
        Response: Renderizado de admin/editar_articulo.html o redirección
            a admin.listar_articulos si la actualización fue exitosa.

    """
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
    """Lista todos los préstamos con filtros y paginación local.

    Obtiene los préstamos desde la API y aplica filtros opcionales por
    estado, usuario y fecha. La paginación se realiza localmente sobre
    los resultados filtrados.

    Query params:
        estado (str): Filtra préstamos por estado (pendiente, aprobado, etc.).
        usuario (str): Filtra préstamos por nombre de usuario.
        fecha (str): Filtra préstamos por fecha de retiro.
        page (int): Número de página. Por defecto 1.

    Returns:
        Response: Renderizado de admin/reservas.html con el listado
            paginado y los filtros activos.

    """
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
    """Lista las penalizaciones con paginación HATEOAS.

    Obtiene el listado paginado de penalizaciones desde la API backend.
    Accesible solo para admin y bibliotecario.

    Query params:
        page (int): Número de página. Por defecto 1.
        usuario (str): Filtra penalizaciones por nombre de usuario.

    Returns:
        Response: Renderizado de admin/penalizaciones.html con el listado
            paginado y metadata de paginación.

    """
    token = session.get("token")
    rol = session.get("rol")
    if not token:
        return redirect(url_for("public.login"))
    if rol not in ["admin", "bibliotecario"]:
        return redirect(url_for("public.home"))

    page = request.args.get("page", 1, type=int)
    offset = calcular_offset(page, DEFAULT_API_LIMIT)
    nombre_usuario = request.args.get("usuario")
    resultado = penalizaciones_servicio.obtener_penalizaciones_paginadas(
        params={"limit": DEFAULT_API_LIMIT, "offset": offset, "usuario": nombre_usuario},
        token=token
    )
    penalizaciones = resultado.get("datos", [])
    pagination = adaptar_pagination_hateoas(resultado)

    return render_template(
        "admin/penalizaciones.html",
        penalizaciones=penalizaciones,
        pagination=pagination,
        mensaje_error=request.args.get("mensaje_error"),
        fetch_error=fetch_error,
    )


@admin_bp.route("/penalizaciones/nueva", methods=["GET", "POST"])
def crear_penalizacion():
    """Renderiza y procesa el formulario de alta de penalización.

    Accesible solo para bibliotecarios (no para admins).
    En GET muestra el formulario con la lista de usuarios disponibles.
    En POST valida los datos y crea la penalización mediante la API.
    Redirige al listado si fue exitoso, o vuelve al formulario con error.

    Form params (POST):
        usuario_id (str): Identificador del usuario a penalizar. Requerido.
        reason (str): Motivo de la penalización. Requerido.
        severidad (str): Nivel de severidad ('baja', 'media', 'alta').
            Opcional, por defecto 'media'.

    Returns:
        Response: Renderizado de admin/penalizaciones_form.html o
            redirección a admin.listar_penalizaciones si fue exitoso.

    """
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
            usuarios = extraer_data_paginada(usuario_servicio.obtener_usuarios(token=token))
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
            usuarios = extraer_data_paginada(usuario_servicio.obtener_usuarios(token=token))
            return render_template(
                "admin/penalizaciones_form.html",
                usuarios=usuarios,
                form_error="No se pudo crear la penalización.",
            )

        return redirect(url_for("admin.listar_penalizaciones"))

    usuarios = extraer_data_paginada(usuario_servicio.obtener_usuarios(token=token))

    return render_template(
        "admin/penalizaciones_form.html",
        usuarios=usuarios,
        form_error=None,
    )


@admin_bp.route("/penalizaciones/<int:id>/levantar", methods=["POST"])
def levantar_penalizacion(id):
    """Levanta (desactiva) una penalización manualmente.

    Envía PATCH /api/penalizaciones/{id} con status 'Levantada'.
    Accesible solo para bibliotecarios.

    Args:
        id (int): Identificador de la penalización a levantar.

    Returns:
        Response: Redirección a admin.listar_penalizaciones tras la operación.

    """
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
    """Renderiza el perfil completo de un usuario para administradores.

    Obtiene los datos del usuario desde la API y los muestra en la
    vista de perfil. Accesible solo para admin y bibliotecario.

    Args:
        id (int): Identificador del usuario a visualizar.

    Returns:
        Response: Renderizado de admin/perfil_usuario.html con los
            datos del usuario.

    """
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
    """Actualiza los datos de un usuario y redirige a su perfil.

    Envía PUT /api/usuarios/{id} con los campos del formulario.
    Accesible solo para bibliotecarios.

    Args:
        id (int): Identificador del usuario a actualizar.

    Form params:
        rol (str): Nuevo rol del usuario.
        email (str): Nuevo email del usuario.
        carrera (str): Nueva carrera del usuario.

    Returns:
        Response: Redirección a admin.usuario_detalle tras la operación.

    """
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
