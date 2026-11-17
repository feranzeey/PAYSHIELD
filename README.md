# PayShield – Secure Fintech Payment Infrastructure

**Building reliable, resilient, and recoverable payment infrastructure.**

PayShield is a containerized fintech payment API built to demonstrate practical backend engineering, database reliability, and DevOps automation.

The project uses FastAPI, PostgreSQL, Docker, and Bash automation to demonstrate payment processing, persistent transaction storage, automated database backups, and disaster recovery.

## Architecture

```text
             Client / Dashboard
                     |
                     v
              FastAPI Payment API
                     |
                     v
                 PostgreSQL
                     |
              Persistent Volume
                     |
                     v
            Automated Backup System
                     |
             Bash + Cron + pg_dump
                     |
                     v
              Backup Archives
                     |
                     v
             Disaster Recovery
                 pg_restore
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Backend development |
| FastAPI | REST API |
| PostgreSQL 16 | Payment data persistence |
| Docker | Application containerization |
| Docker Compose | Multi-container orchestration |
| Uvicorn | ASGI application server |
| Bash | Backup automation |
| Cron | Scheduled database backups |
| pg_dump | Database backup |
| pg_restore | Database recovery |
| Git and GitHub | Version control |

## Key Features

### 1. Payment API
- Create payment transactions.
- Retrieve payment records.
- Retrieve individual payments using their references.
- View payment summary information.
- Handle successful and failed payment scenarios.

### 2. Database Persistence
- PostgreSQL 16 database.
- Persistent Docker volume.
- Database health checks.
- Application startup dependency on database health.

### 3. Automated Database Backups
A Bash script automates PostgreSQL database backups.

Features include:
- Custom timestamped backup filenames.
- PostgreSQL custom-format backups.
- Backup file validation.
- Backup size reporting.
- Automatic cleanup of older backups.
- Backup execution logging.

### 4. Scheduled Backups

Cron schedules database backups daily at 1:00 AM.

Example configuration:

```cron
0 1 * * * cd /home/dadaferanmi/projects/payshield && /usr/bin/bash /home/dadaferanmi/projects/payshield/scripts/backup.sh >> /home/dadaferanmi/projects/payshield/logs/backup.log 2>&1
```

### 5. Disaster Recovery

The project includes a tested PostgreSQL restoration workflow using `pg_restore`.

Recovery verification was performed using a separate temporary database.

**Verified recovery result:**
- Six payment records successfully restored.
- Successful and failed payment records preserved.
- Payment references and transaction details retained.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application homepage |
| GET | `/dashboard` | Payment dashboard |
| GET | `/health` | Application health check |
| GET | `/ready` | Readiness check |
| POST | `/payments` | Create payment |
| GET | `/payments` | Retrieve payments |
| GET | `/payments/{reference}` | Retrieve individual payment |
| GET | `/metrics/summary` | Payment summary |

Interactive API documentation:

`http://localhost:8000/docs`

## Project Structure

```text
payshield/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
├── .env.example
├── scripts/
│   └── backup.sh
├── backups/             # Ignored by Git
└── logs/                # Ignored by Git
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/feranzeey/payshield.git
cd payshield
```

### 2. Configure environment variables

Create `.env` and `.env.docker` using the environment variable names documented below.

Example configuration:

```env
POSTGRES_DB=payshield_db
POSTGRES_USER=payshield_user
POSTGRES_PASSWORD=CHANGE_ME_TO_A_SECURE_PASSWORD
DATABASE_URL=postgresql://payshield_user:CHANGE_ME_TO_A_SECURE_PASSWORD@db:5432/payshield_db
```

Use appropriate local values in both environment files. Never commit real credentials.

### 3. Start the application

```bash
docker compose up -d --build
```

### 4. Check running containers

```bash
docker compose ps
```

### 5. Check API health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "payment-api"
}
```

## Database Backup and Recovery

### Run a manual backup

```bash
/usr/bin/bash scripts/backup.sh
```

### Inspect available backups

```bash
ls -lh backups/
```

### Restore a backup

Create a separate test database:

```bash
docker exec payshield-db createdb \
  -U payshield_user payshield_restore_test
```

Restore the backup:

```bash
docker exec -i payshield-db pg_restore \
  -U payshield_user \
  -d payshield_restore_test \
  --no-owner \
  --no-privileges \
  < backups/YOUR_BACKUP_FILE.dump
```

Verify restored payment records:

```bash
docker exec payshield-db psql \
  -U payshield_user \
  -d payshield_restore_test \
  -c "SELECT COUNT(*) FROM payments;"
```

## Security

- Environment files excluded from Git.
- Database backup files excluded from Git.
- Docker build context excludes local secrets.
- Database credentials supplied through environment variables.
- Persistent database storage configured using Docker volumes.

## Project Verification

The following tests have been performed:

- [x] Dockerized application startup.
- [x] PostgreSQL connectivity.
- [x] Payment record persistence.
- [x] Successful payment testing.
- [x] Failed payment testing.
- [x] Manual database backup.
- [x] Backup file validation.
- [x] Cron scheduling configuration.
- [x] Backup logging.
- [x] Backup retention execution.
- [x] Database restoration.
- [x] Restored payment count verification.
- [x] API health endpoint verification.
- [x] Git and Docker secret exclusion.

## Future Improvements

- [ ] Prometheus and Grafana monitoring.
- [ ] Automated API testing.
- [ ] CI/CD using GitHub Actions.
- [ ] Backup upload to remote object storage.
- [ ] Backup encryption.
- [ ] Database recovery automation.
- [ ] Kubernetes deployment.

## Author

**Oluwaferanmi Dada**

DevOps Engineer | Cloud Infrastructure | Automation | Site Reliability Engineering

- GitHub: https://github.com/feranzeey
- LinkedIn: https://www.linkedin.com/in/dada-oluwaferanmi-devops/

---

PayShield is an independent engineering and portfolio project. It is not presented as a production-certified payment processor or live financial service.
