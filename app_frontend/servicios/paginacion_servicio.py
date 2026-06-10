"""Utilidades reutilizables para paginar listados en vistas."""

DEFAULT_PER_PAGE = 5


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
