## Rutas consolidadas — Frontend

### Roles del sistema

| Rol | Descripción |
|-----|-------------|
| `alumno` | Puede hacer reservas con límites de stock y sujeto a penalizaciones. Tiene `carrera` asociada. |
| `profesor` | Puede hacer reservas sin restricciones ni penalizaciones. |
| `bibliotecario` | Gestión operativa completa: inventario, préstamos, usuarios, penalizaciones y reportes. |
| `admin` | Superusuario para mantenimiento técnico y casos de error. Acceso total. |
---
Esto es algo que habíamos estado conversando con Erick

### Públicas (sin login)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Landing: bloque principal que aparece al entrar a un sitio , ¿cómo funciona?, beneficios, normas resumidas, FAQ, CTA registro |
| `GET` | `/catalogo` | Catálogo de artículos disponibles por tipo/sección, podemos redirigir a la página que ya tienen en fiuba|
| `GET` | `/articulos` | Detalle público de un artículo: nombre, tipo, sección, stock disponible |
| `GET` | `/normas` | Normativas completas  |
| `GET` | `/faq` | Preguntas frecuentes |
| `GET` | `/registro` | Formulario de registro (nombre, email, carrera, contraseña). Al enviar, crea usuario con rol `alumno` por defecto y redirige a `/login`. |
| `GET` | `/login` | Formulario de inicio de sesión. Al enviar, valida credenciales y redirige según rol. |
| `GET` | `/logout` | Cierra sesión activa y redirige a `/` |

---

### Alumno (rol: `alumno`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/alumno/dashboard` | Panel principal: reservas activas y alertas de penalización |
| `GET` | `/alumno/perfil` | Datos personales: nombre, email, carrera |
| `GET` | `/alumno/mis-reservas` | Reservas activas con estado (`pendiente` / `entregado` / `devuelto`). Incluye acción de cancelar reservas pendientes (acción backend). |
| `GET` | `/alumno/mis-reservas/nueva` | Formulario para crear nueva reserva (valida stock y penalizaciones activas). Al enviar, envía la solicitud al backend. |
| `GET` | `/alumno/historial` | Historial completo de reservas pasadas |
| `GET` | `/alumno/penalizaciones` | Penalizaciones activas: motivo, severidad (`baja`/`media`/`alta`), fecha inicio/fin |
| `GET` | `/alumno/reservas/{id}` | Detalle de reserva: estado, fecha retiro/regreso, QR |
| `GET` | `/alumno/reservas/{id}/comprobante` | Ticket de reserva con código QR dinámico (tabla `qr`) |

---

### Profesor (rol: `profesor`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/profesor/dashboard` | Panel principal: reservas activas, accesos rápidos |
| `GET` | `/profesor/perfil` | Datos personales: nombre, email |
| `GET` | `/profesor/mis-reservas` | Reservas activas con estado. Incluye acción de cancelar reservas pendientes (acción backend). |
| `GET` | `/profesor/mis-reservas/nueva` | Formulario para crear nueva reserva (sin límites ni restricciones por penalización). Al enviar, envía la solicitud al backend. |
| `GET` | `/profesor/historial` | Historial completo de reservas pasadas |
| `GET` | `/profesor/reservas/{id}` | Detalle de reserva: estado, fecha retiro/regreso, QR |
| `GET` | `/profesor/reservas/{id}/comprobante` | Ticket de reserva con código QR dinámico |

---

### Bibliotecario (roles: `bibliotecario` / `admin`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/admin/dashboard` | Métricas: préstamos activos, mora, demanda por carrera, inventario crítico |
| `GET` | `/admin/articulos` | ABM de artículos: listado con filtros por tipo/sección. Permite eliminar artículos y acceder a formularios de alta/edición (acciones backend). |
| `GET` | `/admin/articulos/nuevo` | Formulario alta: nombre, tipo, sección, prestación máxima, stock. Al enviar, guarda el nuevo artículo (acción backend). |
| `GET` | `/admin/articulos/{id}/editar` | Formulario edición de artículo para el artículo con id: muestra datos y permite editar. Al enviar, actualiza datos del artículo (incluye `necesita_reparacion`) (acción backend). |
| `GET` | `/admin/reservas` | Lista todos los préstamos con filtros por estado/fecha/usuario |
| `GET` | `/admin/reservas/{id}` | Detalle del préstamo; permite cambiar estado y registrar devolución (`estado_devuelto`) |
| `GET` | `/admin/usuarios` | ABM de usuarios: listado con rol, carrera y email. Permite editar usuarios (acción backend) y acceder a perfiles. |
| `GET` | `/admin/usuarios/{id}` | Perfil completo: historial, penalizaciones y datos de contacto. Desde aquí se pueden modificar datos o rol (acción backend). |
| `GET` | `/admin/penalizaciones` | Lista penalizaciones activas con severidad (campo en el que se define la gravedad) y fechas. Se pueden levantar manualmente (acción backend). |
| `GET` | `/admin/normativas` | ABM de normativas (tabla `normativa`). Permite crear y editar normativas (acciones backend). |
| `GET` | `/admin/reportes` | Panel de reportes para `admin` y `bibliotecario`: gráficos de demanda por carrera |
| `GET` | `/admin/reportes/morosidad` | Reporte de morosidad exportable en PDF |

---

### Error handlers

| Código | Template | Descripción |
|--------|----------|-------------|
| `404` | `404.html` | Ruta no encontrada, link a inicio |
| `500` | `500.html` | Error de servidor, link a inicio |

---

### Notas de implementación

- Todas las rutas usan `url_for()` para links y archivos estáticos
- Los templates heredan de `base.html` con `{% extends "base.html" %}` y `{% block content %}`
- Frontend en puerto `5001`, backend en `5000` — se comunican vía `requests` a `http://localhost:5000`
- Redirección post-login según rol: `alumno` → `/alumno/dashboard`, `profesor` → `/profesor/dashboard`, `bibliotecario`/`admin` → `/admin/dashboard`
- Las rutas de alumno/profesor/admin verifican sesión activa y rol; sin sesión redirigen a `/login`
- El backend valida stock, penalizaciones activas y `prestacion_maxima` antes de confirmar reserva
- El QR se genera en el backend (tabla `qr`) y se incluye en el comprobante
- Las notificaciones por email se disparan desde el backend al confirmar la reserva
