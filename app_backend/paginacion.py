"""Helpers comunes para respuestas paginadas con HATEOAS."""

from urllib.parse import urlencode

DEFAULT_LIMIT = 10
MAX_LIMIT = 100
DEFAULT_OFFSET = 0


def obtener_parametros_paginacion(args):
    """Valida limit/offset desde query params y devuelve valores normalizados."""
    try:
        limit = int(args.get("limit", DEFAULT_LIMIT))
        offset = int(args.get("offset", DEFAULT_OFFSET))
    except (TypeError, ValueError):
        return None, "limit y offset deben ser enteros."

    if limit <= 0:
        return None, "limit debe ser mayor a 0."

    if offset < 0:
        return None, "offset no puede ser negativo."

    return {"limit": min(limit, MAX_LIMIT), "offset": offset}, None


def _query_params_con_paginacion(args, limit, offset):
    """Preserva filtros existentes y reemplaza limit/offset."""
    params = []
    for key, values in args.lists():
        if key in ("limit", "offset"):
            continue
        for value in values:
            params.append((key, value))

    params.extend([("limit", limit), ("offset", offset)])
    return urlencode(params, doseq=True)


def _link_paginado(path, args, limit, offset):
    """Construye un link relativo con filtros y parámetros de paginación."""
    return f"{path}?{_query_params_con_paginacion(args, limit, offset)}"


def construir_respuesta_paginada(data, total, request, limit, offset):
    """Construye el envelope estándar data/pagination/links."""
    data = list(data or [])
    total = max(int(total or 0), 0)
    count = len(data)
    last_offset = ((total - 1) // limit) * limit if total else 0

    prev_offset = max(offset - limit, 0) if offset > 0 else None
    next_offset = offset + limit if offset + count < total else None

    return {
        "data": data,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "count": count,
        },
        "links": {
            "first": _link_paginado(request.path, request.args, limit, 0),
            "prev": (
                _link_paginado(request.path, request.args, limit, prev_offset)
                if prev_offset is not None
                else None
            ),
            "next": (
                _link_paginado(request.path, request.args, limit, next_offset)
                if next_offset is not None
                else None
            ),
            "last": _link_paginado(request.path, request.args, limit, last_offset),
        },
    }
