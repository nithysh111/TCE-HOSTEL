# Database — Phase 2

MySQL schema and seed data for the Hostel Food Intelligence System.

## Quick Setup

```bash
# 1. Create database and all tables
mysql -u root -p < database/schema/schema.sql

# 2. (Optional) Load reference seed data
mysql -u root -p hostel_food_db < database/seeds/seed_data.sql

# 3. (Optional) Load demo users/students with working passwords
cd backend && python seed_data.py
```

## Files

| File | Purpose |
|------|---------|
| `schema/schema.sql` | **Main schema** — all CREATE TABLE scripts |
| `schema/drop_all.sql` | Drop all tables (destructive) |
| `seeds/seed_data.sql` | Holidays and announcements |
| `samples/sample_attendance.csv` | Biometric CSV import format |
| `../docs/DATABASE.md` | ER diagram, table docs, relationships |

## Documentation

See [docs/DATABASE.md](../docs/DATABASE.md) for the full ER diagram and relationship reference.
