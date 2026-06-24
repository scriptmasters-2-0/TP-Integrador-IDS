"""Utilidades reutilizables para paginar listados en vistas."""

DEFAULT_PER_PAGE = 5
DEFAULT_API_LIMIT = 12


def paginas_visibles(pagina_actual, total_paginas):
    """Devuelve páginas compactas para el paginador, usando None como separador."""
    if total_paginas <= 7:
        return list(range(1, total_paginas + 1))

    paginas = [1]
    inicio = max(2, pagina_actual - 1)
    fin = min(total_paginas - 1, pagina_actual + 1)

    if inicio > 2:
        paginas.append(None)

    paginas.extend(range(inicio, fin + 1))

    if fin < total_paginas - 1:
        paginas.append(None)

    paginas.append(total_paginas)
    return paginas


def paginar_lista(items, pagina=1, por_pagina=DEFAULT_PER_PAGE):
    """Corta una lista y devuelve los items de la página junto a metadata."""
    items = list(items or [])
    por_pagina = max(int(por_pagina or DEFAULT_PER_PAGE), 1)
    total_items = len(items)
    total_paginas = max(1, (total_items + por_pagina - 1) // por_pagina)

    try:
        pagina_actual = int(pagina or 1)
    except (TypeError, ValueError):
        pagina_actual = 1

    pagina_actual = min(max(pagina_actual, 1), total_paginas)
    inicio = (pagina_actual - 1) * por_pagina
    fin = inicio + por_pagina

    pagination = {
        "page": pagina_actual,
        "per_page": por_pagina,
        "total_items": total_items,
        "total_pages": total_paginas,
        "first_item": inicio + 1 if total_items else 0,
        "last_item": min(fin, total_items),
        "has_prev": pagina_actual > 1,
        "has_next": pagina_actual < total_paginas,
        "prev_page": pagina_actual - 1,
        "next_page": pagina_actual + 1,
        "pages": paginas_visibles(pagina_actual, total_paginas),
    }
    return items[inicio:fin], pagination


def calcular_offset(pagina=1, por_pagina=DEFAULT_API_LIMIT):
    """Convierte una página visual en offset para la API."""
    try:
        pagina_actual = int(pagina or 1)
    except (TypeError, ValueError):
        pagina_actual = 1

    try:
        limite = int(por_pagina or DEFAULT_API_LIMIT)
    except (TypeError, ValueError):
        limite = DEFAULT_API_LIMIT

    pagina_actual = max(pagina_actual, 1)
    limite = max(limite, 1)
    return (pagina_actual - 1) * limite


def extraer_data_paginada(payload):
    """Obtiene la lista de datos desde una respuesta HATEOAS o una lista legacy."""
    if isinstance(payload, dict):
        data = payload.get("data", [])
        return data if isinstance(data, list) else []
    return payload if isinstance(payload, list) else []


def adaptar_pagination_hateoas(payload, pagina=1):
    """Adapta metadata HATEOAS a la estructura que consumen los templates."""
    if not isinstance(payload, dict):
        return None

    metadata = payload.get("pagination") or {}
    limit = int(metadata.get("limit") or DEFAULT_API_LIMIT)
    offset = int(metadata.get("offset") or 0)
    total_items = int(metadata.get("total") or 0)
    count = int(metadata.get("count") or 0)

    total_pages = max(1, (total_items + limit - 1) // limit)
    page = min(max((offset // limit) + 1, 1), total_pages)
    first_item = offset + 1 if total_items and count else 0
    last_item = min(offset + count, total_items)

    return {
        "page": page,
        "per_page": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "first_item": first_item,
        "last_item": last_item,
        "has_prev": offset > 0,
        "has_next": offset + count < total_items,
        "prev_page": max(page - 1, 1),
        "next_page": min(page + 1, total_pages),
        "pages": paginas_visibles(page, total_pages),
        "links": payload.get("links") or {},
    }
