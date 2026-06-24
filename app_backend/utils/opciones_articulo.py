"""Opciones canonicas para categorizar articulos."""

TIPOS_ARTICULO = [
    {"valor": "Libro", "etiqueta": "Libros"},
    {"valor": "Electronicos", "etiqueta": "Equipos Electrónicos"},
    {"valor": "Herramienta", "etiqueta": "Herramientas"},
    {"valor": "Proyector", "etiqueta": "Proyectores"},
    {"valor": "Accesorios", "etiqueta": "Accesorios y Cables"},
]

SECCIONES_ARTICULO = [
    {"valor": "Biblioteca", "etiqueta": "Biblioteca"},
    {"valor": "Tecnologia", "etiqueta": "Tecnología"},
    {"valor": "Bedelia", "etiqueta": "Bedelía"},
    {"valor": "Laboratorio", "etiqueta": "Laboratorio"},
    {"valor": "Otros", "etiqueta": "Otros"},
]

TIPOS_ARTICULO_VALIDOS = {opcion["valor"] for opcion in TIPOS_ARTICULO}
SECCIONES_ARTICULO_VALIDAS = {opcion["valor"] for opcion in SECCIONES_ARTICULO}


def obtener_opciones_articulo():
    """Devuelve las opciones disponibles para tipo y seccion de articulos."""
    return {
        "tipos": TIPOS_ARTICULO,
        "secciones": SECCIONES_ARTICULO,
    }
