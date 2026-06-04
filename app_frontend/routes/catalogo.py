from flask import Blueprint, request, requests, render_template

BACKEND_URL = "http://127.0.0.1:5001"

@public_bp.route("/catalogo", methods=["GET"])
def mostrar_catalogo():
    "Muestra el catalogo completo de articulos con opcion a filtrar por tipo y seccion"
    
    tipo_actual = request.args.get("tipo", "")
    seccion_actual = request.args.get("seccion", "")

    filtros = {}
    if tipo_actual:
        filtros["tipo"] = tipo_actual
    if seccion_actual:
        filtros["seccion"] = seccion_actual

    try:
        response = requests.get(f"{BACKEND_URL}/api/items", params=filtros)
        if response.status_code == 200:
            articulos = response.json()
        else:
            articulos = []
            print(f"Error Backend")
    except Exception:
        pass

    return render_template(
        "public/catalogo.html",
        articulos=articulos,
        tipo_actual=tipo_actual,
        seccion_actual=seccion_actual
    )

@public_bp.route("/faq", methods=["GET"])
def mostrar_faq():
    return render_template("public/faq.html")

from routes.auth_routes import requiere_auth

@profesor_bp.route("/historial", methods=["GET"])
@requiere_auth(roles="profesor")
def historial():
    "Muestra el historial completo de reservas historicas de un profesor"
    id_profesor = request.user_id
    token = request.headers.get('Autorizacion')
    headers = {'Autorizacion': token}

    try:
        response = requests.get(f"{BACKEND_URL}/users/{id_profesor}/loans")
        if response.status_code == 200:
            reservas_totales = response.json()

            hoy = datetime.now()
            historial = []

            for reserva in reservas_totales:
                fecha_fin = datetime.strptime(reserva["fecha_fin"], '%Y-%m-%d %H:%M:%S')
            
            if fecha_fin < hoy:
                historial.append(reserva)

            return render_template('historial_reservas.html', historial=historial)
        else:
            return render_template('historial_reservas.html', historial=[], error="No se pudo obtener el historial")
        
    except Exception as e:
        print(f"Error inesperado: {e}")
        return render_template('historial_reservas.html', historial=[], error="Error al mostrar el historial")
