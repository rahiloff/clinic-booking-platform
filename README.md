# 🏥 Doctor Booking Platform

A modern, production-grade doctor appointment booking platform for small clinics and independent doctors.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Flutter Web (PWA) |
| Backend | FastAPI (Python 3.12) |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Workers | Celery |
| Proxy | Nginx |
| Infra | Docker Compose |
| Hosting | AWS EC2 |
| Auth | Firebase OTP |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Setup

```bash
# Clone the repository
git clone <repo-url> && cd doctor-booking-app

# Copy environment file
cp .env.example .env
# Edit .env with your values

# Start all services
docker compose up -d

# Check health
curl http://localhost:8000/api/v1/health
```

### Development Commands

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f backend

# Run migrations
docker compose exec backend alembic upgrade head

# Stop services
docker compose down

# Rebuild after dependency changes
docker compose up -d --build backend
```

## Project Structure

```
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── core/     # Config, security
│   │   ├── db/       # Database session
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── auth/     # Authentication
│   │   ├── workers/  # Background jobs
│   │   └── utils/    # Utilities
│   └── alembic/      # DB migrations
├── frontend/         # Flutter Web app
├── infra/            # Nginx, scripts
├── docs/             # Documentation
└── docker-compose.yml
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

Proprietary — All rights reserved.
