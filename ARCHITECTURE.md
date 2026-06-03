
# File structure
├── app_backend
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── db_scripts
│   │   ├── create_seeds.sql
│   │   └── init_db.sql
│   ├── Dockerfile
│   ├── http_codes_and_messages.py
│   ├── pyproject.toml
│   ├── README.md
│   ├── routes
│   │   ├── __init__.py
│   │   ├── auth_route.py
│   │   ├── items_route.py
│   │   ├── loans_route.py
│   │   ├── penalties_route.py
│   │   ├── qr_route.py
│   │   ├── reportes_route.py
│   │   ├── salud_route.py
│   │   └── users_routes.py
│   ├── swagger.yaml
│   ├── uv.lock
│   └── validators.py
├── app_frontend
│   ├── app.py
│   ├── config.py
│   ├── Dockerfile
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── pyproject.toml
│   ├── README.md
│   ├── routes
│   │   ├── __init__.py
│   │   ├── admin_routes.py
│   │   ├── alumno_routes.py
│   │   ├── profesor_routes.py
│   │   └── public_routes.py
│   ├── services
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   ├── images
│   │   │   ├── favicon.png
│   │   │   ├── large_Galeria_PC_06_931d95ba80.jpg
│   │   │   ├── logo-fiuba.png
│   │   │   ├── logo_FIUBA_bco_e004995ae8.png
│   │   │   └── photo-1524995997946-a1c2e315a42f.avif
│   │   └── js
│   │       └── main.js
│   ├── templates
│   │   ├── admin
│   │   │   ├── articulos.html
│   │   │   ├── dashboard.html
│   │   │   └── prestamo_detalle.html
│   │   ├── alumno
│   │   │   ├── comprobante.html
│   │   │   ├── historial.html
│   │   │   └── perfil.html
│   │   ├── layouts
│   │   │   ├── base.html
│   │   │   └── base_dashboard.html
│   │   ├── profesor
│   │   │   ├── dashboard.html
│   │   │   └── mis-reservas
│   │   │       └── nueva.html
│   │   └── public
│   │       ├── index.html
│   │       ├── logout.html
│   │       ├── normas.html
│   │       └── registro.html
│   └── uv.lock
├── docker-compose.yaml
├── init.sh
├── README.md
└── template.env

# DB schema

This database schema is designed for a library or equipment management system. It follows a relational structure focused on tracking users, the items available for loan, the transactions (reservations), and the subsequent management of returns and potential penalties.

### Database Schema Description

* **`usuario`**: The core entity representing any person interacting with the system. It uses an `ENUM` to define access levels (`rol`) and includes authentication fields (`password_hash`) and status tracking (`activo`).
* **`articulos`**: Stores the inventory. It tracks item categorization (`tipo`, `seccion`) and availability (`stock`, `necesita_reparacion`).
* **`reserva`**: The central transactional table connecting `usuario` and `articulos`. It manages the timeline of the loan (`fecha_retiro`, `fecha_regreso`).
* **`estado_devuelto`**: A child table of `reserva` that records the quality of return, specifically noting `dias_retraso` for potential enforcement.
* **`penalizacion`**: Linked to both `usuario` and `reserva`. It tracks disciplinary actions taken against users, including the duration and severity of the sanction.
* **`qr`**: A utility table for verifying transactions. Each reservation generates a unique code that can be flagged as `escaneado` upon successful pickup or return.
* **`normativa`**: An independent table used to store institutional policies or rules, serving as reference material for the system.

---

### Entity-Relationship Representation

The following diagram illustrates the logical flow and relational dependencies of your schema:

```mermaid
erDiagram
    usuario ||--o{ reserva : realiza
    usuario ||--o{ penalizacion : recibe
    articulos ||--o{ reserva : es_reservado
    reserva ||--o| estado_devuelto : tiene
    reserva ||--o{ penalizacion : genera
    reserva ||--o| qr : genera

    usuario {
        int id
        string nombre
        enum rol
    }
    articulos {
        int id
        string nombre_art
        int stock
    }
    reserva {
        int id
        int id_usuario
        int id_reservado
        string estado_reserva
    }
    estado_devuelto {
        int id
        int id_reserva
        int dias_retraso
    }
    penalizacion {
        int id
        int id_usuario
        int id_reserva
        enum severity
    }
    qr {
        int id
        int id_reserva
        string codigo
    }

```

### Technical Observations

* **Normalization**: The schema is well-normalized for a relational system, effectively decoupling the transactional record (`reserva`) from supplementary data like returns or penalties.
* **Extensibility**: The inclusion of a `normativa` table suggests that the system expects dynamic updates to rules.
* **Constraints**: You are using appropriate foreign key constraints to ensure referential integrity, preventing orphans in the `reserva` or `penalizacion` tables.

# Endpoints

This API provides a centralized system for managing inventory, loans, penalties, and user administration. Below is a structured summary of the endpoints.

### 1. Authentication

Handles user sessions.

* **`POST /auth/login`**: Authenticates user credentials and establishes a session.
* *Payload:* `LoginRequest` (username, password)


* **`POST /auth/logout`**: Closes the active session.
* **`GET /auth/me`**: Retrieves the current user's profile and role.

---

### 2. Users

Management of registered users.

* **`GET /users`**: Lists all users (Admin).
* **`POST /users`**: Creates a new user (Admin).
* *Payload:* `UserCreate`


* **`GET /users/{id}`**: Gets details of a specific user.
* **`PUT /users/{id}`**: Updates complete user profile (Admin).
* *Payload:* `UserUpdate`


* **`DELETE /users/{id}`**: Performs a logical deletion (deactivation) of a user.
* **`PATCH /users/{id}/status`**: Partially updates only the active status.
* *Payload:* `UserStatusUpdate`


* **`GET /users/{id}/loans`**: Fetches the personal loan history for a user.
* **`GET /users/{id}/penalties`**: Fetches the penalty history for a user.

---

### 3. Inventory & Materials

Manages catalog and item stock.

* **`GET /items`**: Retrieves item catalog. Supports query filters: `category`, `condition`, `available`.
* **`POST /items`**: Adds a new item to inventory (Admin).
* *Payload:* `ItemCreate`


* **`GET /items/{id}`**: Detailed view of a specific item.
* **`PUT /items/{id}`**: Updates full item information (Admin).
* *Payload:* `ItemUpdate`


* **`DELETE /items/{id}`**: Deletes an item from inventory (Admin).
* **`PATCH /items/{id}/condition`**: Updates the physical condition/repair status of an item.
* *Payload:* `ItemConditionUpdate`



---

### 4. Loans & Reservations

Manages the loan lifecycle.

* **`GET /loans`**: Lists loans. Admins see all, users see their own. Supports filters: `status`, `startDate`, `endDate`.
* **`POST /loans`**: Creates a new reservation request.
* *Payload:* `LoanCreate`


* **`GET /loans/{id}`**: Gets full details of a specific loan.
* **`PATCH /loans/{id}/status`**: Updates the reservation state (Admin).
* *Payload:* `LoanStatusUpdate`



---

### 5. QR Codes

* **`GET /qr/loans/{loan_id}`**: Generates or retrieves the dynamic QR code for an approved loan.

---

### 6. Penalties

Management of disciplinary records.

* **`GET /penalties`**: Lists all penalties (Admin).
* **`POST /penalties`**: Manually creates a penalty (Admin).
* *Payload:* `PenaltyCreate`


* **`GET /penalties/{id}`**: Gets details of a specific penalty.
* **`PUT /penalties/{id}`**: Replaces the full penalty record.
* *Payload:* `PenaltyUpdate`


* **`PATCH /penalties/{id}`**: Partially updates severity, notes, or resolution status.
* *Payload:* `PenaltyPatchUpdate`



---

### 7. Reports & Statistics

* **`GET /reports`**: Generates reports (Admin). Required query param: `type` (dashboard, demand, overdue, history, inventory). Optional param: `format` (json, pdf).

---

### 8. System Health

* **`GET /ping`**: Simple heartbeat check to ensure the backend is operational.

---
