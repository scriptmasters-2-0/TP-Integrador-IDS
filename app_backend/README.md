### Autenticación y Accesos (`/api/auth`)

### Inicialización de Base de Datos

El esquema y los datos iniciales se cargan en el flujo normal con Docker Compose:
`docker-compose.yaml` monta `db_scripts/init_db.sql` y `db_scripts/create_seeds.sql`
en `/docker-entrypoint-initdb.d/` del contenedor MySQL. El backend no ejecuta
`init_database()` automáticamente al arrancar Flask.

* **`POST /api/auth/login`**
Inicia sesión utilizando **flask-login**. Valida credenciales y establece la sesión indicando el rol (alumno/profesor, bibliotecario/admin).
* **`POST /api/auth/logout`**
Cierra la sesión activa del usuario.
* **`GET /api/auth/me`**
Devuelve los datos de perfil y el rol del usuario actualmente autenticado.

### Usuarios (`/api/usuarios`)

* **`GET /api/usuarios`**
Lista los usuarios registrados. **(Admin y bibliotecario)**.
* **`POST /api/usuarios`**
Alta (ABM) de un nuevo usuario. **(Admin y bibliotecario)**.
* **`GET /api/usuarios/{id}`**
Obtiene los detalles de un usuario específico. **(Admin y bibliotecario)**.
* **`PUT /api/usuarios/{id}`**
Modifica los datos de un usuario existente (reemplazo completo).
* **`DELETE /api/usuarios/{id}`**
Baja o desactivación lógica de un usuario (Opción 1).
* **`PATCH /api/usuarios/{id}/status`**
Activa o desactiva a un usuario (Opción 2).
* **`GET /api/usuarios/{id}/reservas`**
Obtiene el historial personal de préstamos/reservas de un alumno y sus estados.
* **`GET /api/usuarios/{id}/penalizaciones`**
Obtiene las penalizaciones vigentes e históricas de un alumno.

### Compatibilidad de Endpoints (`/api/usuario`)

* **`GET /api/usuario`**
Lista usuarios desde la tabla `usuarios` (endpoint agregado en cambios recientes).
* **`GET /api/usuario/<int:usuario_id>`**
Obtiene un usuario puntual desde la tabla `usuarios` por su identificador. **(Admin y bibliotecario)**.

### Inventario y Materiales (`/api/articulos`)

* **`GET /api/articulos`**
Lista el material disponible. Incluye soporte para **filtros por tipo, estado y disponibilidad**. Este endpoint es de **Acceso público** (sin autenticación requerida).
* **`POST /api/articulos`**
Ingreso/creación de un nuevo ítem al inventario. **(Solo Admin)**.
* **`GET /api/articulos/{id}`**
Consulta el detalle, normativas específicas y estado de un ítem particular.
* **`PUT /api/articulos/{id}`**
Actualiza la información general de un ítem. **(Solo Admin)**.
* **`PATCH /api/articulos/{id}/condition`**
Actualiza específicamente el estado o condición física del ítem (ej. disponible, dañado, reparación, dado de baja).
* **`DELETE /api/articulos/{id}`**
Baja definitiva o lógica del ítem del inventario. **(Solo Admin)**.

### Préstamos y Solicitudes (`/api/reservas`)

* **`GET /api/reservas`**
Lista los préstamos. **Admin ve todos, el alumno ve los propios**. Permite filtrar por estado, fechas o disponibilidad.
* **`POST /api/reservas`**
Crea una nueva solicitud de reserva. Valida disponibilidad, sanciones y límites.
* **`GET /api/reservas/{id}`**
Obtiene los detalles completos de un préstamo o solicitud específica.
* **`PATCH /api/reservas/{id}/status`**
Cambia el estado del préstamo (ej. Pendiente -> Aprobado -> Entregado -> Devuelto). **(Solo Admin)**.

### Códigos QR (`/api/qr`)

* **`GET /api/qr/reservas/{reserva_id}`**
Genera o devuelve el código QR dinámico asociado al préstamo aprobado.

### Penalizaciones (`/api/penalizaciones`)

* **`GET /api/penalizaciones`**
Lista general de penalizaciones activas e históricas. **(Solo Admin)**.
* **`POST /api/penalizaciones`**
Genera una nueva penalización manual a un alumno. **(Solo Admin)**.
* **`GET /api/penalizaciones/{id}`**
Obtiene el detalle de una penalización específica.
* **`PUT /api/penalizaciones/{id}`**
Modifica o levanta una penalización reemplazando el registro completo.
* **`PATCH /api/penalizaciones/{id}`**
Actualiza parcialmente los datos de una penalización (ej. ajusta la severidad, agrega notas o la marca como resuelta).
* **`GET /api/penalizaciones?usuario_id={id}`**
Retorna penalizaciones filtradas por usuario usando query param `usuario_id`.

### Reportes y Estadísticas (`/api/reports`)

* **`GET /api/reports`**
Endpoint unificado y centralizado para la generación de reportes (Dashboard, demanda, morosidad, historial, inventario). Se controla mediante **query parameters** (por ejemplo: `?type=overdue&format=pdf` o `?type=dashboard`). **(Solo Admin)**.

### Salud del Sistema

* **`GET /ping`**
Verifica que el backend esté activo y respondiendo.
