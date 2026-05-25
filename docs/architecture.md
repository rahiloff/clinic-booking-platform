# Doctor Booking Platform — Architecture Documentation

## System Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Cloudflare (CDN/WAF)                   │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                    Nginx (Reverse Proxy)                  │
│                    Port 80 / 443                          │
└────────┬────────────────────────────────┬────────────────┘
         │                                │
         │ /api/*                         │ /* (future)
         ▼                                ▼
┌─────────────────┐              ┌─────────────────┐
│  FastAPI Backend │              │  Flutter Web     │
│  Port 8000       │              │  (Static PWA)    │
└───┬─────────┬───┘              └─────────────────┘
    │         │
    ▼         ▼
┌────────┐ ┌────────┐    ┌──────────────┐
│Postgres│ │ Redis  │◄───│ Celery Worker │
│  :5432 │ │ :6379  │    │ (Background)  │
└────────┘ └────────┘    └──────────────┘
```

## Design Principles

### 1. Clean Architecture (Layered)

```
Routes (api/)  →  Services (services/)  →  Models (models/)
      ↑                    ↑                      ↑
  Schemas (schemas/)   Dependencies (deps.py)   Database (db/)
```

**Rules:**
- Routes only handle HTTP concerns (parse request, return response)
- Services contain ALL business logic
- Models define database structure
- Schemas define API contracts (request/response shapes)
- No business logic in routes or models

### 2. Dependency Injection

FastAPI's `Depends()` is used for:
- Database sessions
- Current user resolution
- Role-based access control
- Service instantiation

### 3. API Versioning

All APIs are prefixed with `/api/v1/`. When breaking changes are needed:
- Create `/api/v2/` router
- Keep v1 alive with deprecation notices
- Migrate clients gradually

### 4. Database Conventions

| Convention | Example |
|------------|---------|
| Table names | `users`, `appointments` (plural, snake_case) |
| Primary keys | UUID v4 |
| Foreign keys | `user_id`, `doctor_id` |
| Timestamps | `created_at`, `updated_at` (timezone-aware) |
| Indexes | On FKs, unique constraints, common query columns |
| Soft delete | `deleted_at` column (nullable) |

### 5. Security Layers

1. **Cloudflare**: DDoS protection, WAF rules
2. **Nginx**: Rate limiting, security headers, SSL termination
3. **FastAPI**: CORS, input validation, JWT verification
4. **Database**: Parameterized queries (SQLAlchemy), row-level locking

## File Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Models | Singular | `user.py`, `appointment.py` |
| Schemas | Singular | `user.py`, `appointment.py` |
| Endpoints | Plural | `users.py`, `appointments.py` |
| Services | Singular | `user_service.py`, `booking_service.py` |

## Environment Strategy

| Environment | Database | Redis | Debug |
|------------|----------|-------|-------|
| development | Local Docker | Local Docker | true |
| staging | RDS | ElastiCache | false |
| production | RDS (Multi-AZ) | ElastiCache | false |
