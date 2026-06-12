# Phase 1 — Complete Folder Structure

**AI-Based Hostel Food Intelligence & Management System**

This document defines the full project layout for frontend, backend, database, ML, configuration, services, utilities, and deployment. **No application code is written in Phase 1** — only structure and purpose definitions.

---

## High-Level Architecture

```
hostel-food-intelligence/
├── docs/                   # Project documentation
├── database/               # Database schema, migrations, seeds
├── deployment/             # Docker, Nginx, deploy scripts
├── backend/                # Flask REST API + ML integration
├── frontend/               # React (Vite) SPA
├── README.md               # Project overview & quick start
└── .gitignore              # Git ignore rules
```

---

## Root Level

| Path | Purpose |
|------|---------|
| `README.md` | Project overview, tech stack, setup instructions, and demo credentials. Entry point for new developers. |
| `.gitignore` | Excludes `venv/`, `node_modules/`, `.env`, `__pycache__/`, build artifacts, and local database files from version control. |

---

## `docs/` — Documentation

| Path | Purpose |
|------|---------|
| `docs/PHASE1_STRUCTURE.md` | This file. Defines folder layout and the role of every directory and planned file. |
| `docs/ARCHITECTURE.md` | *(Phase 2+)* System architecture diagrams, data flow, and module interaction. |
| `docs/API.md` | *(Phase 3+)* REST API endpoint reference with request/response examples. |
| `docs/DATABASE.md` | *(Phase 2+)* ER diagram, table relationships, and indexing strategy. |
| `docs/ML_PIPELINE.md` | *(Phase 5+)* ML training, evaluation metrics, and prediction workflow. |
| `docs/DEPLOYMENT.md` | *(Phase 6+)* Production deployment guide (Docker, Nginx, environment variables). |

---

## `database/` — Database Layer

Centralizes all database-related artifacts separate from the Flask app.

| Path | Purpose |
|------|---------|
| `database/schema/schema.sql` | MySQL DDL: `CREATE DATABASE`, tables, indexes, constraints, and enums. Source of truth for production schema. |
| `database/migrations/` | Versioned schema change scripts (e.g. `001_initial.sql`, `002_add_index.sql`). Applied in order during upgrades. |
| `database/seeds/` | Initial/demo data SQL scripts (admin user, sample students, menus). Run after schema creation. |
| `database/samples/sample_attendance.csv` | Example biometric CSV format for attendance import testing. |

**Planned tables (schema):**

| Table | Module |
|-------|--------|
| `users` | Authentication (admin / student roles) |
| `students` | Student Information System |
| `attendance` | Biometric Attendance Integration |
| `leave_requests` | Leave & holiday stay requests |
| `food_menus` | Food Menu Management |
| `complaints` | Complaint Management |
| `announcements` | Announcements |
| `food_predictions` | ML prediction output storage |
| `food_wastage` | Food wastage reports |

---

## `deployment/` — Deployment & DevOps

| Path | Purpose |
|------|---------|
| `deployment/docker/Dockerfile.backend` | Multi-stage Docker image for Flask API (Python, dependencies, Gunicorn). |
| `deployment/docker/Dockerfile.frontend` | Docker image for React build served via Nginx. |
| `deployment/docker/docker-compose.yml` | Orchestrates MySQL, backend, frontend, and optional ML training container. |
| `deployment/nginx/nginx.conf` | Reverse proxy: `/api` → backend, `/` → frontend, static uploads. |
| `deployment/scripts/setup.sh` | First-time server setup (install deps, create DB, run migrations). |
| `deployment/scripts/deploy.sh` | Pull, build, migrate, and restart services. |
| `deployment/scripts/backup_db.sh` | Scheduled MySQL dump for backups. |

---

## `backend/` — Flask REST API

### Root backend files

| Path | Purpose |
|------|---------|
| `backend/run.py` | Application entry point. Starts Flask dev server or wires Gunicorn in production. |
| `backend/requirements.txt` | Pinned Python dependencies (Flask, SQLAlchemy, JWT, ML libs). |
| `backend/.env.example` | Template for environment variables (secrets, DB URL, JWT keys). |
| `backend/seed_data.py` | Python script to populate demo data via ORM (alternative to SQL seeds). |

### `backend/app/` — Application package

| Path | Purpose |
|------|---------|
| `backend/app/__init__.py` | Application factory (`create_app`). Registers blueprints, extensions, CORS, and DB init. |
| `backend/app/extensions.py` | Shared Flask extensions: `db` (SQLAlchemy), `jwt` (JWTManager). Initialized once, imported everywhere. |

### `backend/app/config/` — Configuration

| Path | Purpose |
|------|---------|
| `backend/app/config/__init__.py` | Exports `Config`, `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`. |
| `backend/app/config/base.py` | Base settings: secret keys, JWT expiry, upload limits, ML model path. |
| `backend/app/config/development.py` | Dev overrides: debug mode, SQLite fallback, verbose logging. |
| `backend/app/config/production.py` | Prod overrides: MySQL URI, secure cookies, no debug. |

### `backend/app/models/` — SQLAlchemy ORM Models

Each file maps one database table to a Python class with `to_dict()` for JSON serialization.

| Path | Purpose |
|------|---------|
| `backend/app/models/__init__.py` | Imports and exports all models for `db.create_all()` and migrations. |
| `backend/app/models/user.py` | `users` — email, password hash, role (admin/student). |
| `backend/app/models/student.py` | `students` — roll no, name, department, room, hostel block. |
| `backend/app/models/attendance.py` | `attendance` — biometric entry/exit logs, status. |
| `backend/app/models/leave_request.py` | `leave_requests` — leave and holiday-stay requests. |
| `backend/app/models/food_menu.py` | `food_menus` — daily/special meal menus. |
| `backend/app/models/complaint.py` | `complaints` — student complaints and status. |
| `backend/app/models/announcement.py` | `announcements` — notices with priority and expiry. |
| `backend/app/models/food_prediction.py` | `food_predictions` — ML output (breakfast/lunch/dinner counts). |
| `backend/app/models/food_wastage.py` | `food_wastage` — prepared vs consumed vs wasted quantities. |

### `backend/app/routes/` — REST API Blueprints

Thin controllers: validate input, call services, return JSON. One blueprint per domain.

| Path | Purpose |
|------|---------|
| `backend/app/routes/auth.py` | `POST /api/auth/login`, `register`, `GET /me`. |
| `backend/app/routes/students.py` | Student CRUD, roll-no search, room allocation. |
| `backend/app/routes/attendance.py` | CSV/API import, attendance log listing. |
| `backend/app/routes/occupancy.py` | Live occupancy summary, inside/outside/on-leave lists, trends. |
| `backend/app/routes/menus.py` | Menu CRUD, today/weekly/special endpoints. |
| `backend/app/routes/complaints.py` | Submit complaint, list, update status. |
| `backend/app/routes/announcements.py` | Announcement CRUD. |
| `backend/app/routes/leave.py` | Leave request submit, admin approve/reject. |
| `backend/app/routes/predictions.py` | Food prediction, history, wastage reports. |
| `backend/app/routes/analytics.py` | Dashboard aggregates for charts. |

### `backend/app/services/` — Business Logic

Reusable domain logic decoupled from HTTP layer.

| Path | Purpose |
|------|---------|
| `backend/app/services/occupancy_service.py` | Computes inside/outside/on-leave counts and occupancy trends from attendance + leave data. |
| `backend/app/services/attendance_service.py` | CSV parsing, API batch import, attendance log queries. |
| `backend/app/services/menu_service.py` | *(Planned)* Menu validation, image handling, weekly aggregation. |
| `backend/app/services/complaint_service.py` | *(Planned)* Complaint ID generation, status transitions. |
| `backend/app/services/prediction_service.py` | *(Planned)* Wrapper that loads ML model and persists predictions. |
| `backend/app/services/analytics_service.py` | *(Planned)* Aggregates data for dashboard charts. |

### `backend/app/utils/` — Utilities

| Path | Purpose |
|------|---------|
| `backend/app/utils/decorators.py` | `@admin_required`, `@student_required` JWT role guards. |
| `backend/app/utils/helpers.py` | Date parsing, file upload helpers, complaint ID generator. |
| `backend/app/utils/validators.py` | *(Planned)* Shared input validation functions. |
| `backend/app/utils/response.py` | *(Planned)* Standardized JSON success/error response builders. |

### `backend/app/middleware/` — Request Middleware

| Path | Purpose |
|------|---------|
| `backend/app/middleware/error_handler.py` | *(Planned)* Global 404/500/validation error handlers. |
| `backend/app/middleware/request_logger.py` | *(Planned)* Request/response logging for audit and debugging. |

### `backend/app/schemas/` — Request/Response Schemas

| Path | Purpose |
|------|---------|
| `backend/app/schemas/auth_schema.py` | *(Planned)* Login/register payload validation. |
| `backend/app/schemas/student_schema.py` | *(Planned)* Student create/update field rules. |
| `backend/app/schemas/menu_schema.py` | *(Planned)* Menu payload validation. |

### `backend/ml/` — Machine Learning Module

| Path | Purpose |
|------|---------|
| `backend/ml/generate_dataset.py` | Synthetic dataset generator (Pandas/NumPy) for training. |
| `backend/ml/train_model.py` | Random Forest Regressor training, evaluation (MAE, RMSE, R²), Joblib save. |
| `backend/ml/prediction_service.py` | Loads saved model; predicts breakfast/lunch/dinner student counts. |
| `backend/ml/food_prediction_model.joblib` | Trained model artifact (generated, not committed). |
| `backend/ml/synthetic_food_data.csv` | Generated training CSV (optional, for inspection). |

### `backend/uploads/` — File Storage

| Path | Purpose |
|------|---------|
| `backend/uploads/menus/` | Uploaded menu images served at `/uploads/menus/<filename>`. |

### `backend/logs/` — Application Logs

| Path | Purpose |
|------|---------|
| `backend/logs/.gitkeep` | Runtime log files (e.g. `app.log`, `error.log`) written here in production. |

### `backend/tests/` — Backend Tests

| Path | Purpose |
|------|---------|
| `backend/tests/unit/` | Unit tests for services, utils, ML pipeline. |
| `backend/tests/integration/` | API endpoint tests with test database. |
| `backend/tests/conftest.py` | *(Planned)* Pytest fixtures (app, client, auth tokens). |

---

## `frontend/` — React (Vite) SPA

### Root frontend files

| Path | Purpose |
|------|---------|
| `frontend/package.json` | NPM dependencies and scripts (`dev`, `build`, `preview`). |
| `frontend/vite.config.js` | Vite config, dev server port, API proxy to Flask. |
| `frontend/tailwind.config.js` | Tailwind theme (colors, fonts, custom utilities). |
| `frontend/postcss.config.js` | PostCSS plugins for Tailwind. |
| `frontend/index.html` | HTML shell; mounts React at `#root`. |

### `frontend/public/` — Static Assets

| Path | Purpose |
|------|---------|
| `frontend/public/vite.svg` | Favicon / default logo. |
| `frontend/public/robots.txt` | *(Optional)* Search engine directives. |

### `frontend/src/` — Source Code

| Path | Purpose |
|------|---------|
| `frontend/src/main.jsx` | React DOM entry; renders `<App />`. |
| `frontend/src/App.jsx` | Router setup, protected routes, role-based navigation. |
| `frontend/src/index.css` | Tailwind directives and global component classes. |

### `frontend/src/assets/` — Media

| Path | Purpose |
|------|---------|
| `frontend/src/assets/images/` | Logos, icons, illustrations used in UI. |

### `frontend/src/components/` — Reusable UI

| Path | Purpose |
|------|---------|
| `frontend/src/components/layout/Layout.jsx` | Sidebar navigation, header, `<Outlet />` for nested routes. |
| `frontend/src/components/layout/ProtectedRoute.jsx` | Redirects unauthenticated users; enforces admin/student role. |
| `frontend/src/components/common/StatCard.jsx` | Dashboard metric card (title, value, icon). |
| `frontend/src/components/common/LoadingSpinner.jsx` | Loading state indicator. |
| `frontend/src/components/common/StatusBadge.jsx` | Color-coded status pill (Open, Resolved, inside, etc.). |
| `frontend/src/components/charts/ChartCard.jsx` | Wrapper for Chart.js charts with title and fixed height. |
| `frontend/src/components/charts/OccupancyChart.jsx` | *(Planned)* Reusable occupancy line/bar chart. |
| `frontend/src/components/charts/PredictionChart.jsx` | *(Planned)* Food prediction bar chart. |

### `frontend/src/pages/` — Route Pages

#### Admin pages (`pages/admin/`)

| Path | Purpose |
|------|---------|
| `Dashboard.jsx` | Management overview: occupancy cards, trend charts, complaint/wastage stats. |
| `Occupancy.jsx` | Live inside/outside/on-leave lists and weekly/monthly charts. |
| `Students.jsx` | Roll-no search, student list, room allocation view. |
| `Menus.jsx` | Add/update/delete daily and special menus. |
| `Predictions.jsx` | AI food predictions, history chart, wastage entry. |
| `Complaints.jsx` | View and update complaint status. |
| `Announcements.jsx` | Create, edit, delete announcements. |
| `Leave.jsx` | Approve/reject student leave requests. |
| `Attendance.jsx` | Import biometric CSV, view attendance logs. |

#### Student pages (`pages/student/`)

| Path | Purpose |
|------|---------|
| `Dashboard.jsx` | Today's menu, recent announcements, quick links. |
| `Menu.jsx` | Today, weekly, and special meal views. |
| `Complaints.jsx` | Submit and track complaints. |
| `Announcements.jsx` | View active announcements. |
| `Leave.jsx` | Submit leave and holiday-stay requests. |

#### Shared pages

| Path | Purpose |
|------|---------|
| `frontend/src/pages/Login.jsx` | JWT login form for admin and student. |

### `frontend/src/context/` — React Context

| Path | Purpose |
|------|---------|
| `frontend/src/context/AuthContext.jsx` | Global auth state: user, token, login/logout, role flags. |

### `frontend/src/services/` — API Client

| Path | Purpose |
|------|---------|
| `frontend/src/services/api.js` | Axios instance with JWT interceptor; grouped API methods per module. |

### `frontend/src/hooks/` — Custom Hooks

| Path | Purpose |
|------|---------|
| `frontend/src/hooks/useAuth.js` | *(Planned)* Thin wrapper around `AuthContext`. |
| `frontend/src/hooks/useFetch.js` | *(Planned)* Generic data-fetching hook with loading/error state. |

### `frontend/src/utils/` — Frontend Utilities

| Path | Purpose |
|------|---------|
| `frontend/src/utils/date.js` | *(Planned)* Date formatting helpers. |
| `frontend/src/utils/format.js` | *(Planned)* Number/text formatting. |

### `frontend/src/constants/` — Constants

| Path | Purpose |
|------|---------|
| `frontend/src/constants/roles.js` | *(Planned)* `ADMIN`, `STUDENT` role constants. |
| `frontend/src/constants/complaintCategories.js` | *(Planned)* Complaint category enum. |
| `frontend/src/constants/mealTypes.js` | *(Planned)* Breakfast, Lunch, Dinner constants. |

### `frontend/dist/` — Build Output

Generated by `npm run build`. Served in production. **Not committed to git.**

---

## Module-to-Folder Mapping

| System Module | Backend | Frontend | Database | ML |
|---------------|---------|----------|----------|-----|
| Biometric Attendance | `routes/attendance`, `services/attendance_service` | `pages/admin/Attendance` | `attendance` table | — |
| Live Occupancy | `routes/occupancy`, `services/occupancy_service` | `pages/admin/Occupancy`, `Dashboard` | `attendance`, `leave_requests` | — |
| AI Food Prediction | `routes/predictions` | `pages/admin/Predictions` | `food_predictions` | `ml/*` |
| Student Information | `routes/students` | `pages/admin/Students` | `students` | — |
| Food Menu | `routes/menus` | `pages/admin/Menus`, `pages/student/Menu` | `food_menus` | — |
| Complaints | `routes/complaints` | `pages/admin/Complaints`, `pages/student/Complaints` | `complaints` | — |
| Announcements | `routes/announcements` | `pages/admin/Announcements`, `pages/student/Announcements` | `announcements` | — |
| Auth | `routes/auth` | `pages/Login`, `context/AuthContext` | `users` | — |
| Analytics | `routes/analytics` | `pages/admin/Dashboard` | All tables | — |

---

## Data Flow (Phase 1 Concept)

```
Biometric Device / CSV
        │
        ▼
  attendance (DB) ──► occupancy_service ──► Occupancy Dashboard
        │                        │
        │                        ▼
        │              prediction_service (ML)
        │                        │
        ▼                        ▼
  leave_requests            food_predictions
        │                        │
        └──────────┬─────────────┘
                   ▼
            analytics/dashboard
                   │
                   ▼
              React Frontend (Chart.js)
```

---

## Phase 1 Deliverables Checklist

- [x] Root project layout defined
- [x] `database/` layer separated from backend
- [x] `deployment/` scaffold for Docker/Nginx/scripts
- [x] Backend layered: routes → services → models
- [x] Frontend layered: pages → components → services
- [x] ML module isolated under `backend/ml/`
- [x] Configuration split (`config/`, `.env.example`)
- [x] Tests and logs directories reserved
- [ ] **Phase 2:** Implement database schema and models
- [ ] **Phase 3:** Implement backend APIs
- [ ] **Phase 4:** Implement frontend pages
- [ ] **Phase 5:** Implement ML pipeline
- [ ] **Phase 6:** Wire integration and deployment

---

## Next Step

**Phase 2** will implement the MySQL database schema, SQLAlchemy models, and seed data — using the paths defined above.
