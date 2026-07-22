# Dental Radiograph Encryption Service

## Overview
This project is a backend web application designed to securely handle dental radiograph uploads. It focuses on protecting sensitive medical data by encrypting image files at rest and decrypting them only when accessed by authenticated users.

The application is containerized and deployed on **Google Cloud**, demonstrating secure backend development, cloud deployment, and production-oriented security practices.

## Tech Stack
- Python 3
- FastAPI
- SQLAlchemy
- SQLite (local) / Cloud SQL (production)
- Docker
- Google Cloud Run
- Google Cloud Storage
- Symmetric encryption (Fernet)
- JWT-based authentication

## Core Features
- Secure user authentication and authorization
- Encrypted storage of uploaded radiograph images
- Unique, non-guessable filenames for stored files
- On-demand decryption and secure file serving
- Containerized application deployed to Google Cloud Run

## Security Design
- Radiographs are encrypted immediately upon upload and stored encrypted at rest
- Encryption keys are injected via environment variables
- Decryption occurs only for authenticated, authorized users
- Database access is mediated through an ORM to reduce injection risk
- Sensitive files are never stored in plaintext

## Architecture Overview
- FastAPI REST API running in a Docker container
- Google Cloud Run for serverless container execution
- Cloud SQL for relational data persistence
- Google Cloud Storage for encrypted file storage
- Environment-based configuration for local vs cloud execution

## Deployment
The application can be deployed to **Google Cloud Run** using a containerized workflow. Secrets and configuration are provided via environment variables, with production deployment intended to integrate a managed secrets service and key rotation.

### Portfolio Mode: Seeded Demo
For a low-cost portfolio demo, run the app on Cloud Run with SQLite in `/tmp` and a seeded demo account. This avoids Cloud SQL and Google Cloud Storage charges while still demonstrating FastAPI, SQLAlchemy, authentication, encrypted uploads, Docker, and Cloud Run.

This mode uses disposable fake data. If Cloud Run restarts, the SQLite database and uploaded files may disappear; on the next startup the app recreates the tables and reseeds the demo account.

Demo credentials:

```text
Email: demo@dental-records.dev
Password: DemoPassword123!
```

Required environment variables:

```bash
ENVIRONMENT=local
DATABASE_URL=sqlite:////tmp/dental_app.db
LOCAL_UPLOAD_DIR=/tmp/uploads
SEED_DEMO_DATA=true
DEMO_EMAIL=demo@dental-records.dev
DEMO_PASSWORD=DemoPassword123!
ENCRYPTION_KEY=<fernet-key>
JWT_KEY=<jwt-secret>
CANONICAL_HOST=dental-records.com
REDIRECT_HOSTS=www.dental-records.com,app.dental-records.com,dental-app-39943357835.us-central1.run.app
```

Generate local secrets:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Example Cloud Run deployment:

```bash
gcloud run deploy dental-radiograph-demo \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=local,DATABASE_URL=sqlite:////tmp/dental_app.db,LOCAL_UPLOAD_DIR=/tmp/uploads,SEED_DEMO_DATA=true,DEMO_EMAIL=demo@dental-records.dev,DEMO_PASSWORD=DemoPassword123!,ENCRYPTION_KEY=<fernet-key>,JWT_KEY=<jwt-secret>,CANONICAL_HOST=dental-records.com,REDIRECT_HOSTS=www.dental-records.com,app.dental-records.com,dental-app-39943357835.us-central1.run.app
```

### Local Docker
Create a `.env` file from `.env.example`, fill in `ENCRYPTION_KEY` and `JWT_KEY`, then run:

```bash
docker-compose up --build
```

The app will be available at `http://localhost:8000`.

### Production Mode
For a real production deployment with persistent data, set `DATABASE_URL` to a managed Postgres/Cloud SQL connection string, set `ENVIRONMENT=cloud`, and provide `BUCKET_NAME` for Google Cloud Storage.

## What I’d Improve Next
- Integrate Google Secret Manager with automatic key rotation
- Add role-based access control (RBAC)
- Implement audit logging for file access
- Add automated security and integration tests
- Harden CORS and rate limiting for public endpoints

## Author
Aaron Brown
MS in Software Development — Boston University
