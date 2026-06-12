# AI-Based Hostel Food Intelligence & Management System

A full-stack web application for colleges and universities to manage hostel occupancy, biometric attendance, food planning, AI-driven meal predictions, complaints, announcements, and student services.

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React (Vite), Tailwind CSS, Axios, React Router, Chart.js |
| Backend | Python Flask, SQLAlchemy, JWT Authentication, REST APIs |
| Database | MySQL |
| ML | Pandas, NumPy, Scikit-learn, Random Forest Regressor, Joblib |

## Project Structure

```
hostel-food-intelligence/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── routes/          # REST API blueprints
│   │   ├── services/        # Business logic (occupancy, attendance)
│   │   └── utils/           # Helpers & decorators
│   ├── ml/                  # ML pipeline (dataset, training, prediction)
│   ├── schema.sql           # MySQL database schema
│   ├── seed_data.py         # Demo data seeder
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Admin & Student pages
│   │   ├── services/        # Axios API client
│   │   └── context/         # Auth context
│   └── package.json
└── README.md
```

## Modules

1. **Biometric Attendance** — CSV/API import, entry/exit tracking, occupancy determination
2. **Live Occupancy Dashboard** — Real-time inside/outside/on-leave stats with Chart.js
3. **AI Food Prediction** — Random Forest model predicting breakfast/lunch/dinner attendance
4. **Student Information** — Search by roll number, room allocation, profile view
5. **Food Menu Management** — Daily/weekly/special menus with CRUD
6. **Complaint Management** — Student submission, admin status updates
7. **Announcements** — Priority-based notices with expiry dates

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 1. Database Setup

```bash
mysql -u root -p < database/schema/schema.sql
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MySQL credentials
```

Train the ML model:

```bash
cd ml
python train_model.py
cd ..
```

Seed demo data:

```bash
python seed_data.py
```

Start the API server:

```bash
python run.py
```

API runs at `http://localhost:5000`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@hostel.edu | admin123 |
| Student | cs001@student.edu | student123 |

## API Endpoints

| Module | Endpoint | Description |
|--------|----------|-------------|
| Auth | `POST /api/auth/login` | JWT login |
| Auth | `POST /api/auth/register` | Student registration |
| Occupancy | `GET /api/occupancy/summary` | Live occupancy stats |
| Occupancy | `GET /api/occupancy/inside` | Students inside hostel |
| Attendance | `POST /api/attendance/import/csv` | Import biometric CSV |
| Students | `GET /api/students/search/:roll_no` | Search by roll number |
| Menus | `GET /api/menus/today` | Today's food menu |
| Predictions | `GET /api/predictions/food` | AI meal predictions |
| Complaints | `POST /api/complaints/` | Submit complaint |
| Announcements | `GET /api/announcements/` | List announcements |
| Analytics | `GET /api/analytics/dashboard` | Dashboard analytics |

## ML Model

The food prediction system uses a **Random Forest Regressor** (MultiOutput) trained on synthetic historical data with features:

- Total students, inside/outside counts, leave requests
- Weekend and holiday flags
- Historical attendance patterns

Outputs: predicted breakfast, lunch, and dinner student counts.

```bash
# Generate synthetic dataset
cd backend/ml && python generate_dataset.py

# Train and evaluate model
python train_model.py
```

Model is saved to `backend/ml/food_prediction_model.joblib` and loaded automatically by the prediction service.

## License

MIT
