WASCO ONLINE WATER BILLING MANAGEMENT SYSTEM

This version matches your current table structures exactly.

IMPORTANT:
There is no app.py in this MVC version. Start the system with:

python run.py

SETUP STEPS

1. Open the folder in VS Code.

2. Create a virtual environment:

   python -m venv venv

3. Activate it:

   venv\Scripts\activate

4. Install requirements:

   pip install -r requirements.txt

5. PostgreSQL:
   Create database:
   CREATE DATABASE wasco_main_db;

   Then run:
   database/postgres_full_setup.sql

6. MySQL:
   Create database:
   CREATE DATABASE wasco_fragment_db;

   Then run:
   database/mysql_fragment_setup.sql

7. Copy .env.example and rename it to .env.
   Confirm passwords and usernames are correct.

8. Run:

   python run.py

9. Open:

   http://127.0.0.1:5000

INITIAL ACCOUNTS

Administrator:
username: admin
password: Admin@2026

Branch Manager:
username: manager
password: Manager@2026

Customer:
username: customer
password: Customer@2026

ASSIGNING BILLS

Sign in as administrator, open the Administration page, then use the Assign Customer Bill form.
The form records a meter reading first, then assigns a bill to the selected customer.
Customers will see the assigned bill in their customer portal.


WATER USAGE DISPLAY

When the administrator assigns a bill, the system records previous and current meter readings.
Water usage is calculated automatically in the database as:
current_reading - previous_reading

The calculated usage appears in:
- Admin bill list
- Customer dashboard
- Customer meter reading history
- Manager monthly and district reports


ASSIGN WATER USAGE

The administrator does not manually type the bill amount.
The administrator selects the customer, enters previous and current meter readings, and due date.
The system calculates:
usage_units = current_reading - previous_reading
amount_owed = usage_units * billing_rate

The customer portal then shows:
- billing month
- water usage
- amount owed
- amount paid
- remaining balance
- payment status


BRANCH PERFORMANCE

Sign in as branch manager:
username: manager
password: Manager@2026

The manager dashboard now shows:
- overall system totals
- branch/district performance
- water usage per branch
- total billed per branch
- total paid per branch
- outstanding balances
- collection rate
- daily performance
- service report performance


BRANCH MODULE SETUP

Because this version includes branch management, run these upgrade files after your normal database setup:

PostgreSQL:
database/postgres_branch_upgrade.sql

MySQL:
database/mysql_branch_upgrade.sql

The system now supports:
- adding branches from the admin dashboard
- assigning customers to branches
- assigning branch managers to branches
- branch manager performance filtered by assigned branch
- branch-level billing, usage, collection and outstanding balance reports
