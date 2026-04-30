WASCO Hosted Deployment + Database Sync Ready

START COMMAND FOR RAILWAY
gunicorn run:app --bind 0.0.0.0:$PORT

REQUIRED RAILWAY VARIABLES

SECRET_KEY=any-long-random-secret
FLASK_ENV=production

PostgreSQL main database:
DATABASE_URL=postgresql://user:password@host:5432/database
POSTGRES_SSLMODE=require

MySQL reporting database:
Either use:
MYSQL_URL=mysql://user:password@host:3306/database

Or split variables:
MYSQL_HOST=your-mysql-host
MYSQL_PORT=3306
MYSQL_DB=railway
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_SSL=false

IMPORTANT:
If your database password contains special characters:
# becomes %23
@ becomes %40

DATABASE SETUP

1. Restore/create your PostgreSQL main DB first.

2. On Railway MySQL, run:
database/mysql_hosted_reporting_schema.sql

3. Deploy app to Railway.

4. Log in as admin.

5. Click:
Synchronize Reporting Database → Sync Now

This copies PostgreSQL data into MySQL:
districts, branches, customers, users, billing rates, meter readings, bills, payments, notifications, leakage reports.

FILES UPDATED

- run.py
- Procfile
- requirements.txt
- .env.example
- app/models/db.py
- app/services/sync_service.py
- app/controllers/admin_controller.py
- app/templates/admin/dashboard.html
- database/mysql_hosted_reporting_schema.sql
