"""Definición de constantes de códigos HTTP y mensajes de respuesta.

Centraliza los códigos de estado HTTP y los mensajes asociados
utilizados en las respuestas de la API.
"""

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_INTERNAL_SERVER_ERROR = 500


MSG_OK = "OK"
MSG_CREATED = "Creado"
MSG_NO_CONTENT = "Sin contenido"
MSG_BAD_REQUEST = "Solicitud incorrecta"
MSG_UNAUTHORIZED = "No autorizado"
MSG_FORBIDDEN = "Prohibido"
MSG_NOT_FOUND = "No encontrado"
MSG_CONFLICT = "Conflicto"
MSG_INTERNAL_SERVER_ERROR = "Error interno del servidor"


MSG_DB_CONNECTION_FAILED = "No se pudo conectar a la base de datos"
