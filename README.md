# Hipótesis y Supuestos

* **Autogestión y Responsabilidad:** El acceso directo del alumno a su historial y penalizaciones fomentará el cuidado del material y reducirá significativamente las consultas administrativas presenciales.
* **Eficiencia Administrativa y Usabilidad:** Una interfaz intuitiva para la gestión de inventarios y devoluciones simplificará la transición digital y evitará que los administradores necesiten capacitación técnica compleja.
* **Decisión Administrativa Informada:** El registro detallado del historial de comportamiento y devoluciones permitirá a los administradores tomar decisiones precisas al aceptar o rechazar solicitudes.
* **Integridad de Datos:** El uso de transacciones en MySQL garantizará que no se produzcan conflictos de reserva sobre un mismo recurso técnico en tiempo real.

# Alcance del Proyecto

* **Control Centralizado de Inventario:** Base de datos relacional (MySQL) para gestionar el ciclo de vida del stock (herramientas, libros, placas) desde su ingreso hasta su retiro o reparación.
* **Administración Integral de Usuarios:** Módulo de gestión para el alta, baja y modificación (ABM) de perfiles, diferenciando entre roles de alumno y administrador.
* **Seguridad y Control de Acceso:** Endpoints en el backend protegidos mediante autenticación para asegurar que las funciones críticas y datos sensibles estén limitados por el rol del usuario.
* **Controlador y Lógica de Préstamos:** Sistema que valida límites de pedidos permitidos y verifica penalizaciones vigentes antes de confirmar una reserva.
* **Gestor de Perfil del Alumno:** Interfaz donde el usuario puede visualizar su historial personal, el estado de sus pedidos (Pendiente, Entregado, Devuelto) y sus penalizaciones.
* **Notificaciones y Comprobantes:** Integración de un servicio de correo para el envío automático de un ticket de reserva, el cual incluirá las condiciones del préstamo y un código QR dinámico para la validación al momento de la entrega/devolución.
* **Interfaz de Consulta Pública:** Sección web accesible sin necesidad de autenticación para consultar el material disponible y las normativas de la biblioteca técnica.
* **Dashboard y Reportes Administrativos:** Generación de gráficos de demanda de materiales por carrera y exportación de reportes de morosidad en formato PDF para los administradores.
