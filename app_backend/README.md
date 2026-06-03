### Autenticación y Accesos (`/api/auth`)

* **`POST /api/auth/login`**
Inicia sesión utilizando **flask-login**. Valida credenciales y establece la sesión indicando el rol (alumno/docente, bibliotecario/admin).
* **`POST /api/auth/logout`**
Cierra la sesión activa del usuario.
* **`GET /api/auth/me`**
Devuelve los datos de perfil y el rol del usuario actualmente autenticado.

### Usuarios (`/api/users`)

* **`GET /api/users`**
Lista los usuarios registrados. **(Solo Admin)**.
* **`POST /api/users`**
Alta (ABM) de un nuevo usuario. **(Solo Admin)**.
* **`GET /api/users/{id}`**
Obtiene los detalles de un usuario específico.
* **`PUT /api/users/{id}`**
Modifica los datos de un usuario existente (reemplazo completo).
* **`DELETE /api/users/{id}`**
Baja o desactivación lógica de un usuario (Opción 1).
* **`PATCH /api/users/{id}/status`**
Activa o desactiva a un usuario (Opción 2).
* **`GET /api/users/{id}/loans`**
Obtiene el historial personal de préstamos/pedidos de un alumno y sus estados.
* **`GET /api/users/{id}/penalties`**
Obtiene las penalizaciones vigentes e históricas de un alumno.

### Compatibilidad de Endpoints (`/api/user`)

* **`GET /api/user`**
Lista usuarios desde la tabla `users` (endpoint agregado en cambios recientes).
* **`GET /api/user/<int:user_id>`**
Obtiene un usuario puntual desde la tabla `users` por su identificador.

### Inventario y Materiales (`/api/items`)

* **`GET /api/items`**
Lista el material disponible. Incluye soporte para **filtros por tipo, estado y disponibilidad**. Este endpoint es de **Acceso público** (sin autenticación requerida).
* **`POST /api/items`**
Ingreso/creación de un nuevo ítem al inventario. **(Solo Admin)**.
* **`GET /api/items/{id}`**
Consulta el detalle, normativas específicas y estado de un ítem particular.
* **`PUT /api/items/{id}`**
Actualiza la información general de un ítem. **(Solo Admin)**.
* **`PATCH /api/items/{id}/condition`**
Actualiza específicamente el estado o condición física del ítem (ej. disponible, dañado, reparación, dado de baja).
* **`DELETE /api/items/{id}`**
Baja definitiva o lógica del ítem del inventario. **(Solo Admin)**.

### Préstamos y Solicitudes (`/api/loans`)

* **`GET /api/loans`**
Lista los préstamos. **Admin ve todos, el alumno ve los propios**. Permite filtrar por estado, fechas o disponibilidad.
* **`POST /api/loans`**
Crea una nueva solicitud de reserva. Valida disponibilidad, sanciones y límites.
* **`GET /api/loans/{id}`**
Obtiene los detalles completos de un préstamo o solicitud específica.
* **`PATCH /api/loans/{id}/status`**
Cambia el estado del préstamo (ej. Pendiente -> Aprobado -> Entregado -> Devuelto). **(Solo Admin)**.

### Códigos QR (`/api/qr`)

* **`GET /api/qr/loans/{loan_id}`**
Genera o devuelve el código QR dinámico asociado al préstamo aprobado.

### Penalizaciones (`/api/penalties`)

* **`GET /api/penalties`**
Lista general de penalizaciones activas e históricas. **(Solo Admin)**.
* **`POST /api/penalties`**
Genera una nueva penalización manual a un alumno. **(Solo Admin)**.
* **`GET /api/penalties/{id}`**
Obtiene el detalle de una penalización específica.
* **`PUT /api/penalties/{id}`**
Modifica o levanta una penalización reemplazando el registro completo.
* **`PATCH /api/penalties/{id}`**
Actualiza parcialmente los datos de una penalización (ej. ajusta la severidad, agrega notas o la marca como resuelta).
* **`GET /api/penalties?user_id={id}`**
Retorna penalizaciones filtradas por usuario usando query param `user_id`.

### Reportes y Estadísticas (`/api/reports`)

* **`GET /api/reports`**
Endpoint unificado y centralizado para la generación de reportes (Dashboard, demanda, morosidad, historial, inventario). Se controla mediante **query parameters** (por ejemplo: `?type=overdue&format=pdf` o `?type=dashboard`). **(Solo Admin)**.

### Salud del Sistema

* **`GET /ping`**
Verifica que el backend esté activo y respondiendo.
