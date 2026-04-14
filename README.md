# ComicAI

A web application to display a comic book library.

## Stack
- **Backend:** Python (FastAPI)
- **Frontend:** Vue.js
- **Database:** MySQL
- **Containers:** Docker
- **Testing:** TDD (pytest, Jest)
- **RBAC:** Role Based Access Control

## Roles
- **super admin:** can create only admins
- **admin:** can create other users except super admins, and can add, change, delete comics
- **friends:** can see the comics
- **visitors:** cannot see anything

## Setup
1. Copy `.env.example` to `.env` and fill in secrets.
2. Run `docker-compose up --build` to start all services.
3. Access backend at `http://localhost:8000`, frontend at `http://localhost:8080`.

## Testing
- Backend: `docker-compose exec backend pytest`
- Frontend: `docker-compose exec frontend npm run test:unit`

## Notes
- Store secrets in `.env` (never commit to GitHub).
- Use `.env.example` as a template for secrets.
- RBAC and authentication are enforced on all endpoints.
