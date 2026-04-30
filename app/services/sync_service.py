from app.models.db import get_main_db, get_reporting_db


def _table_exists_mysql(cur, table_name):
    cur.execute("SHOW TABLES LIKE %s", (table_name,))
    return cur.fetchone() is not None


def sync_postgres_to_mysql():
    """
    Copies the latest data from PostgreSQL main DB to MySQL reporting DB.

    Order matters because of foreign keys:
    districts -> branches -> customers -> users -> billing_rates -> meter_readings
    -> bills -> payments -> notifications -> leakage_reports
    """
    pg = get_main_db()
    pg_cur = pg.cursor()

    mysql = get_reporting_db()
    my_cur = mysql.cursor()

    synced = {
        "districts": 0,
        "branches": 0,
        "customers": 0,
        "users": 0,
        "billing_rates": 0,
        "meter_readings": 0,
        "bills": 0,
        "payments": 0,
        "notifications": 0,
        "leakage_reports": 0,
    }

    try:
        # Districts
        pg_cur.execute("SELECT district_id, district_name FROM districts ORDER BY district_id")
        for r in pg_cur.fetchall():
            my_cur.execute("""
                INSERT INTO districts (district_id, district_name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE district_name = VALUES(district_name)
            """, (r["district_id"], r["district_name"]))
            synced["districts"] += 1

        # Branches
        if _table_exists_mysql(my_cur, "branches"):
            pg_cur.execute("""
                SELECT branch_id, branch_name, district_id, location, phone, email, created_at
                FROM branches
                ORDER BY branch_id
            """)
            for r in pg_cur.fetchall():
                my_cur.execute("""
                    INSERT INTO branches
                    (branch_id, branch_name, district_id, location, phone, email, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        branch_name = VALUES(branch_name),
                        district_id = VALUES(district_id),
                        location = VALUES(location),
                        phone = VALUES(phone),
                        email = VALUES(email),
                        created_at = VALUES(created_at)
                """, (
                    r["branch_id"], r["branch_name"], r["district_id"], r["location"],
                    r["phone"], r["email"], r["created_at"]
                ))
                synced["branches"] += 1

        # Customers
        pg_cur.execute("""
            SELECT customer_id, account_number, full_name, phone, email, address,
                   district_id, branch_id, created_at
            FROM customers
            ORDER BY customer_id
        """)
        for r in pg_cur.fetchall():
            my_cur.execute("""
                INSERT INTO customers
                (customer_id, account_number, full_name, phone, email, address, district_id, branch_id, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    account_number = VALUES(account_number),
                    full_name = VALUES(full_name),
                    phone = VALUES(phone),
                    email = VALUES(email),
                    address = VALUES(address),
                    district_id = VALUES(district_id),
                    branch_id = VALUES(branch_id),
                    created_at = VALUES(created_at)
            """, (
                r["customer_id"], r["account_number"], r["full_name"],
                r["phone"], r["email"], r["address"], r["district_id"],
                r.get("branch_id"), r["created_at"]
            ))
            synced["customers"] += 1

        # Users
        if _table_exists_mysql(my_cur, "users"):
            pg_cur.execute("""
                SELECT user_id, customer_id, username, password_hash, role, branch_id, created_at
                FROM users
                ORDER BY user_id
            """)
            for r in pg_cur.fetchall():
                my_cur.execute("""
                    INSERT INTO users
                    (user_id, customer_id, username, password_hash, role, branch_id, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        customer_id = VALUES(customer_id),
                        username = VALUES(username),
                        password_hash = VALUES(password_hash),
                        role = VALUES(role),
                        branch_id = VALUES(branch_id),
                        created_at = VALUES(created_at)
                """, (
                    r["user_id"], r.get("customer_id"), r["username"],
                    r["password_hash"], r["role"], r.get("branch_id"), r["created_at"]
                ))
                synced["users"] += 1

        # Billing rates
        pg_cur.execute("""
            SELECT rate_id, rate_tier, min_usage, max_usage, cost_per_unit
            FROM billing_rates
            ORDER BY rate_id
        """)
        for r in pg_cur.fetchall():
            my_cur.execute("""
                INSERT INTO billing_rates
                (rate_id, rate_tier, min_usage, max_usage, cost_per_unit)
                VALUES (%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    rate_tier = VALUES(rate_tier),
                    min_usage = VALUES(min_usage),
                    max_usage = VALUES(max_usage),
                    cost_per_unit = VALUES(cost_per_unit)
            """, (
                r["rate_id"], r["rate_tier"], r["min_usage"],
                r["max_usage"], r["cost_per_unit"]
            ))
            synced["billing_rates"] += 1

        # Meter readings
        pg_cur.execute("""
            SELECT reading_id, customer_id, reading_month, previous_reading,
                   current_reading, reading_date
            FROM meter_readings
            ORDER BY reading_id
        """)
        for r in pg_cur.fetchall():
            my_cur.execute("""
                INSERT INTO meter_readings
                (reading_id, customer_id, reading_month, previous_reading, current_reading, reading_date)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    customer_id = VALUES(customer_id),
                    reading_month = VALUES(reading_month),
                    previous_reading = VALUES(previous_reading),
                    current_reading = VALUES(current_reading),
                    reading_date = VALUES(reading_date)
            """, (
                r["reading_id"], r["customer_id"], r["reading_month"],
                r["previous_reading"], r["current_reading"], r["reading_date"]
            ))
            synced["meter_readings"] += 1

        # Bills
        pg_cur.execute("""
            SELECT bill_id, customer_id, reading_id, billing_month, total_amount,
                   payment_status, due_date, created_at
            FROM bills
            ORDER BY bill_id
        """)
        for r in pg_cur.fetchall():
            my_cur.execute("""
                INSERT INTO bills
                (bill_id, customer_id, reading_id, billing_month, total_amount, payment_status, due_date, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    customer_id = VALUES(customer_id),
                    reading_id = VALUES(reading_id),
                    billing_month = VALUES(billing_month),
                    total_amount = VALUES(total_amount),
                    payment_status = VALUES(payment_status),
                    due_date = VALUES(due_date),
                    created_at = VALUES(created_at)
            """, (
                r["bill_id"], r["customer_id"], r["reading_id"], r["billing_month"],
                r["total_amount"], r["payment_status"], r["due_date"], r["created_at"]
            ))
            synced["bills"] += 1

        # Payments
        pg_cur.execute("""
            SELECT payment_id, bill_id, customer_id, amount_paid,
                   payment_method, payment_reference, payment_date
            FROM payments
            ORDER BY payment_id
        """)
        for r in pg_cur.fetchall():
            my_cur.execute("""
                INSERT INTO payments
                (payment_id, bill_id, customer_id, amount_paid, payment_method, payment_reference, payment_date)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    bill_id = VALUES(bill_id),
                    customer_id = VALUES(customer_id),
                    amount_paid = VALUES(amount_paid),
                    payment_method = VALUES(payment_method),
                    payment_reference = VALUES(payment_reference),
                    payment_date = VALUES(payment_date)
            """, (
                r["payment_id"], r["bill_id"], r["customer_id"], r["amount_paid"],
                r["payment_method"], r["payment_reference"], r["payment_date"]
            ))
            synced["payments"] += 1

        # Notifications
        if _table_exists_mysql(my_cur, "notifications"):
            pg_cur.execute("""
                SELECT notification_id, customer_id, bill_id, message,
                       notification_type, status, sent_at
                FROM notifications
                ORDER BY notification_id
            """)
            for r in pg_cur.fetchall():
                my_cur.execute("""
                    INSERT INTO notifications
                    (notification_id, customer_id, bill_id, message, notification_type, status, sent_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        customer_id = VALUES(customer_id),
                        bill_id = VALUES(bill_id),
                        message = VALUES(message),
                        notification_type = VALUES(notification_type),
                        status = VALUES(status),
                        sent_at = VALUES(sent_at)
                """, (
                    r["notification_id"], r["customer_id"], r.get("bill_id"),
                    r["message"], r["notification_type"], r["status"], r["sent_at"]
                ))
                synced["notifications"] += 1

        # Leakage reports
        if _table_exists_mysql(my_cur, "leakage_reports"):
            pg_cur.execute("""
                SELECT report_id, customer_id, location, description, report_status, reported_at
                FROM leakage_reports
                ORDER BY report_id
            """)
            for r in pg_cur.fetchall():
                my_cur.execute("""
                    INSERT INTO leakage_reports
                    (report_id, customer_id, location, description, report_status, reported_at)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        customer_id = VALUES(customer_id),
                        location = VALUES(location),
                        description = VALUES(description),
                        report_status = VALUES(report_status),
                        reported_at = VALUES(reported_at)
                """, (
                    r["report_id"], r["customer_id"], r["location"],
                    r["description"], r["report_status"], r["reported_at"]
                ))
                synced["leakage_reports"] += 1

        mysql.commit()
        return synced

    except Exception:
        mysql.rollback()
        raise

    finally:
        pg_cur.close()
        pg.close()
        my_cur.close()
        mysql.close()
