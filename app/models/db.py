import os
import psycopg2
import psycopg2.extras
import pymysql


def get_main_db():
    """
    Main transactional database.

    Hosted deployment:
      DATABASE_URL=postgresql://user:password@host:port/dbname

    Local fallback:
      POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    """
    database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

    if database_url:
        return psycopg2.connect(
            database_url,
            sslmode=os.getenv("POSTGRES_SSLMODE", "require"),
            cursor_factory=psycopg2.extras.RealDictCursor
        )

    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "wasco_main_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "Barbie@5"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def get_reporting_db():
    """
    MySQL reporting/fragment database.

    Hosted deployment:
      MYSQL_URL=mysql://user:password@host:port/dbname

    Or split vars:
      MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD
    """
    mysql_url = os.getenv("MYSQL_URL")

    if mysql_url:
        from urllib.parse import urlparse, unquote

        parsed = urlparse(mysql_url)
        return pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=(parsed.path or "/").lstrip("/"),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            ssl={"ssl": {}} if os.getenv("MYSQL_SSL", "false").lower() == "true" else None
        )

    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DB", "wasco_fragment_db"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "Barbie@5"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        ssl={"ssl": {}} if os.getenv("MYSQL_SSL", "false").lower() == "true" else None
    )
