# Phase 2 — Database Design

**AI-Based Hostel Food Intelligence & Management System**

Canonical schema file: [`database/schema/schema.sql`](../database/schema/schema.sql)

---

## ER Diagram

```mermaid
erDiagram
    users ||--o| students : "has account"
    users ||--o{ leave_requests : "reviews"
    users ||--o{ food_menus : "creates"
    users ||--o{ complaints : "resolves"
    users ||--o{ announcements : "publishes"
    users ||--o{ meal_attendance : "records"
    users ||--o{ food_wastage : "records"

    students ||--o{ attendance : "roll_no"
    students ||--o{ leave_requests : "roll_no"
    students ||--o{ complaints : "roll_no"

    users {
        int id PK
        varchar roll_no UK
        varchar email UK
        varchar password_hash
        enum role
        tinyint is_active
        datetime last_login_at
        datetime created_at
        datetime updated_at
    }

    students {
        int id PK
        int user_id FK UK
        varchar roll_no UK
        varchar name
        varchar department
        tinyint year
        enum gender
        varchar phone_number
        varchar parent_contact
        varchar room_number
        varchar hostel_block
        tinyint is_active
        datetime created_at
        datetime updated_at
    }

    attendance {
        int id PK
        varchar roll_no FK
        datetime entry_time
        datetime exit_time
        date attendance_date
        enum status
        enum source
        datetime created_at
    }

    leave_requests {
        int id PK
        varchar roll_no FK
        date start_date
        date end_date
        text reason
        enum leave_type
        enum status
        int reviewed_by FK
        datetime reviewed_at
        datetime created_at
        datetime updated_at
    }

    food_menus {
        int id PK
        date menu_date
        enum meal_type
        varchar menu_title
        text menu_items
        tinyint is_special
        text description
        varchar image_path
        int created_by FK
        datetime created_at
        datetime updated_at
    }

    complaints {
        int id PK
        varchar complaint_id UK
        varchar roll_no FK
        enum category
        text description
        enum status
        int resolved_by FK
        datetime resolved_at
        datetime created_at
        datetime updated_at
    }

    announcements {
        int id PK
        varchar title
        text description
        enum priority
        date expiry_date
        int created_by FK
        datetime created_at
        datetime updated_at
    }

    holidays {
        int id PK
        date holiday_date UK
        varchar holiday_name
        varchar description
        datetime created_at
    }

    food_predictions {
        int id PK
        date prediction_date UK
        int predicted_breakfast
        int predicted_lunch
        int predicted_dinner
        int actual_breakfast
        int actual_lunch
        int actual_dinner
        int total_students
        int students_inside
        int students_outside
        int students_on_leave
        tinyint is_weekend
        tinyint is_holiday
        varchar model_version
        datetime created_at
    }

    meal_attendance {
        int id PK
        date attendance_date
        enum meal_type
        int student_count
        int recorded_by FK
        datetime created_at
        datetime updated_at
    }

    food_wastage {
        int id PK
        date report_date
        enum meal_type
        int prepared_quantity
        int consumed_quantity
        int wasted_quantity
        text notes
        int recorded_by FK
        datetime created_at
    }
```

---

## Entity Relationship Summary

| Parent | Child | Relationship | FK Column | On Delete |
|--------|-------|--------------|-----------|-----------|
| `users` | `students` | One-to-One (optional) | `students.user_id` | SET NULL |
| `users` | `leave_requests` | One-to-Many | `leave_requests.reviewed_by` | SET NULL |
| `users` | `food_menus` | One-to-Many | `food_menus.created_by` | SET NULL |
| `users` | `complaints` | One-to-Many | `complaints.resolved_by` | SET NULL |
| `users` | `announcements` | One-to-Many | `announcements.created_by` | SET NULL |
| `users` | `meal_attendance` | One-to-Many | `meal_attendance.recorded_by` | SET NULL |
| `users` | `food_wastage` | One-to-Many | `food_wastage.recorded_by` | SET NULL |
| `students` | `attendance` | One-to-Many | `attendance.roll_no` | CASCADE |
| `students` | `leave_requests` | One-to-Many | `leave_requests.roll_no` | CASCADE |
| `students` | `complaints` | One-to-Many | `complaints.roll_no` | CASCADE |

**Standalone tables** (no foreign keys): `holidays`, `food_predictions`

---

## Tables by Module

### Authentication & Student Information

| Table | Module | Description |
|-------|--------|-------------|
| `users` | Auth | Login accounts — admin and student roles |
| `students` | Student Info | Profiles, departments, room allocation |

### Module 1 — Biometric Attendance

| Table | Description |
|-------|-------------|
| `attendance` | Entry/exit times, daily status (`inside` / `outside` / `on_leave`), import source |

### Module 2 — Live Occupancy Dashboard

No dedicated table. Occupancy is **derived** at query time from:

- `attendance` — latest status per student per day
- `leave_requests` — approved leaves overlapping today
- `students` — total student count

### Module 3 — AI/ML Food Prediction

| Table | Description |
|-------|-------------|
| `food_predictions` | Predicted and actual breakfast/lunch/dinner counts per day |
| `meal_attendance` | Actual students who ate each meal (feeds `actual_*` columns) |
| `food_wastage` | Prepared vs consumed vs wasted quantities |
| `holidays` | Holiday calendar for `is_holiday` ML feature |

### Module 5 — Food Menu Management

| Table | Description |
|-------|-------------|
| `food_menus` | Daily menus, special/festival meals, optional images |

### Module 6 — Complaint Management

| Table | Description |
|-------|-------------|
| `complaints` | Categories, descriptions, status workflow |

### Module 7 — Announcements

| Table | Description |
|-------|-------------|
| `announcements` | Title, description, priority, optional expiry |

### Leave Management (Student + Admin)

| Table | Description |
|-------|-------------|
| `leave_requests` | Regular leave and holiday-stay requests with approval workflow |

---

## Table Reference

### `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | Surrogate key |
| roll_no | VARCHAR(20) | UNIQUE, NULL | Student roll number (NULL for admin) |
| email | VARCHAR(120) | UNIQUE, NOT NULL | Login email |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt/PBKDF2 hash |
| role | ENUM | NOT NULL, DEFAULT 'student' | `admin` or `student` |
| is_active | TINYINT(1) | NOT NULL, DEFAULT 1 | Account enabled flag |
| last_login_at | DATETIME | NULL | Last successful login |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation |
| updated_at | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Last modification |

### `students`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | Surrogate key |
| user_id | INT | FK → users.id, UNIQUE | Linked login account |
| roll_no | VARCHAR(20) | UNIQUE, NOT NULL | University roll number |
| name | VARCHAR(100) | NOT NULL | Full name |
| department | VARCHAR(100) | NOT NULL | e.g. CSE, ECE |
| year | TINYINT | NOT NULL, CHECK 1–5 | Academic year |
| gender | ENUM | NOT NULL | Male, Female, Other |
| phone_number | VARCHAR(15) | NULL | Student mobile |
| parent_contact | VARCHAR(15) | NULL | Parent/guardian contact |
| room_number | VARCHAR(20) | NULL | Allocated room |
| hostel_block | VARCHAR(50) | NULL | Block name (A, B, C) |
| is_active | TINYINT(1) | NOT NULL, DEFAULT 1 | Enrollment active flag |

### `attendance`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | Surrogate key |
| roll_no | VARCHAR(20) | FK → students.roll_no | Student identifier |
| entry_time | DATETIME | NULL | Biometric entry timestamp |
| exit_time | DATETIME | NULL | Biometric exit timestamp |
| attendance_date | DATE | NOT NULL | Date of record |
| status | ENUM | NOT NULL | `inside`, `outside`, `on_leave` |
| source | ENUM | NOT NULL, DEFAULT 'biometric' | `biometric`, `manual`, `api` |

### `leave_requests`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK | Surrogate key |
| roll_no | VARCHAR(20) | FK → students.roll_no | Applicant |
| start_date | DATE | NOT NULL | Leave start |
| end_date | DATE | NOT NULL, CHECK ≥ start_date | Leave end |
| reason | TEXT | NULL | Reason for leave |
| leave_type | ENUM | DEFAULT 'regular' | `regular` or `holiday_stay` |
| status | ENUM | DEFAULT 'pending' | `pending`, `approved`, `rejected` |
| reviewed_by | INT | FK → users.id | Admin who reviewed |
| reviewed_at | DATETIME | NULL | Review timestamp |

### `food_menus`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK | Surrogate key |
| menu_date | DATE | NOT NULL | Date of menu |
| meal_type | ENUM | NOT NULL | Breakfast, Lunch, Dinner |
| menu_title | VARCHAR(200) | NOT NULL | Menu heading |
| menu_items | TEXT | NOT NULL | Comma-separated items |
| is_special | TINYINT(1) | DEFAULT 0 | Festival/special meal flag |
| description | TEXT | NULL | Additional notes |
| image_path | VARCHAR(255) | NULL | Uploaded image path |
| created_by | INT | FK → users.id | Admin who created |

**Unique:** `(menu_date, meal_type)` — one menu per meal per day.

### `complaints`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK | Surrogate key |
| complaint_id | VARCHAR(20) | UNIQUE, NOT NULL | Human-readable ID (e.g. CMP-20260611-A1B2C3) |
| roll_no | VARCHAR(20) | FK → students.roll_no | Complainant |
| category | ENUM | NOT NULL | Electrical, WiFi, Food Quality, etc. |
| description | TEXT | NOT NULL | Issue details |
| status | ENUM | DEFAULT 'Open' | Open → In Progress → Resolved |
| resolved_by | INT | FK → users.id | Admin who resolved |
| resolved_at | DATETIME | NULL | Resolution timestamp |

### `announcements`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK | Surrogate key |
| title | VARCHAR(200) | NOT NULL | Announcement heading |
| description | TEXT | NOT NULL | Full message body |
| priority | ENUM | DEFAULT 'medium' | low, medium, high |
| expiry_date | DATE | NULL | Auto-hide after this date |
| created_by | INT | FK → users.id | Publishing admin |

### `holidays`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK | Surrogate key |
| holiday_date | DATE | UNIQUE, NOT NULL | Calendar date |
| holiday_name | VARCHAR(150) | NOT NULL | e.g. Republic Day |
| description | VARCHAR(255) | NULL | Optional note |

### `food_predictions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK | Surrogate key |
| prediction_date | DATE | UNIQUE, NOT NULL | Date of forecast |
| predicted_breakfast | INT | NOT NULL | ML predicted count |
| predicted_lunch | INT | NOT NULL | ML predicted count |
| predicted_dinner | INT | NOT NULL | ML predicted count |
| actual_breakfast | INT | NULL | Recorded actual count |
| actual_lunch | INT | NULL | Recorded actual count |
| actual_dinner | INT | NULL | Recorded actual count |
| total_students | INT | NULL | Input feature snapshot |
| students_inside | INT | NULL | Input feature snapshot |
| students_outside | INT | NULL | Input feature snapshot |
| students_on_leave | INT | NULL | Input feature snapshot |
| is_weekend | TINYINT(1) | DEFAULT 0 | Input feature |
| is_holiday | TINYINT(1) | DEFAULT 0 | Input feature |
| model_version | VARCHAR(50) | NULL | ML model version tag |

### `meal_attendance`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK | Surrogate key |
| attendance_date | DATE | NOT NULL | Date |
| meal_type | ENUM | NOT NULL | Breakfast, Lunch, Dinner |
| student_count | INT | NOT NULL, CHECK ≥ 0 | Students who ate |
| recorded_by | INT | FK → users.id | Recording admin |

**Unique:** `(attendance_date, meal_type)`

### `food_wastage`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK | Surrogate key |
| report_date | DATE | NOT NULL | Report date |
| meal_type | ENUM | NOT NULL | Breakfast, Lunch, Dinner |
| prepared_quantity | INT | NOT NULL, CHECK ≥ 0 | Servings prepared |
| consumed_quantity | INT | NOT NULL, CHECK ≥ 0 | Servings eaten |
| wasted_quantity | INT | NOT NULL, CHECK ≥ 0 | Servings wasted |
| notes | TEXT | NULL | Optional remarks |
| recorded_by | INT | FK → users.id | Recording admin |

**Unique:** `(report_date, meal_type)`

---

## Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| attendance | idx_attendance_roll_date | roll_no, attendance_date | Per-student daily lookup |
| attendance | idx_attendance_status | attendance_date, status | Occupancy queries |
| leave_requests | idx_leave_active | status, start_date, end_date | Active leave filter |
| students | idx_students_room | hostel_block, room_number | Room allocation view |
| food_menus | idx_menu_special | is_special, menu_date | Special meals listing |
| announcements | idx_announcement_active | expiry_date, created_at | Active announcements |

---

## How to Apply

```bash
# Create database and all 11 tables
mysql -u root -p < database/schema/schema.sql

# Load holidays and announcements
mysql -u root -p hostel_food_db < database/seeds/seed_data.sql
```

---

## Phase 2 Checklist

- [x] ER Diagram (Mermaid)
- [x] 11 tables covering all 7 modules
- [x] Foreign key relationships defined
- [x] CREATE TABLE scripts in `database/schema/schema.sql`
- [x] Seed data SQL in `database/seeds/seed_data.sql`
- [x] Sample attendance CSV in `database/samples/`
- [ ] **Phase 3:** SQLAlchemy models and Flask APIs
