import os
import psycopg2
import psycopg2.extras
import pymysql


def get_main_db():
    database_url = os.getenv("DATABASE_URL")

    # ✅ Railway / Supabase / Production
    if database_url:
        return psycopg2.connect(
            database_url,
            sslmode="require",
            cursor_factory=psycopg2.extras.RealDictCursor
        )

    # ✅ Local fallback (for development)
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "wasco_main_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "Barbie@5"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def get_reporting_db():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DB", "wasco_fragment_db"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "Barbie@5"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
