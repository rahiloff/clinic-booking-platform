#!/bin/bash
set -e

echo "=== Doctor Booking Backend Bootstrap ==="

cd "$(dirname "$0")/.."

echo "1. Activating virtual environment..."
source venv/bin/activate

echo "2. Rebuilding Database Schema (Dropping all tables)..."
# Using alembic downgrade base to drop tables cleanly
alembic downgrade base || echo "No tables to drop or downgrade failed (safe to ignore on fresh DB)"

echo "3. Running Migrations..."
alembic upgrade head

echo "4. Seeding Deterministic Demo Data..."
PYTHONPATH=. python scripts/seed_db.py

echo "=== Bootstrap Complete! ==="
echo "You can now run: uvicorn app.main:app --reload"
