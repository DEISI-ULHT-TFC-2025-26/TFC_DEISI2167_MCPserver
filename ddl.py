import sqlite3

def create_database(db_path="db/mcp.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # -------------------------
    # CREATE TABLES
    # -------------------------

    # Table to store database connection information
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS db_connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,     -- Unique ID
        name TEXT NOT NULL,                       -- Human-readable name
        dialect TEXT NOT NULL,                     -- e.g., postgresql, mysql, sqlite, mssql
        driver TEXT,                               -- e.g., psycopg2, pymysql, pyodbc
        host TEXT,                                 -- hostname or IP
        port INTEGER,                              -- port number
        username TEXT,                             -- DB username
        password TEXT,                             -- DB password (should be encrypted in production)
        database_name TEXT NOT NULL,               -- DB name/schema
        environment TEXT DEFAULT 'prod',           -- dev/staging/prod
        ssl_mode TEXT,                             -- e.g., require, verify-full
        created_by TEXT,                            -- who added this connection
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, -- timestamp of creation
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP, -- last update timestamp
        description TEXT                            -- optional notes about the connection
    )
    """)
    
    cursor.execute("""
    INSERT INTO db_connections (
        name, dialect, driver, host, port, username, password, database_name, environment, ssl_mode, created_by, description
    ) VALUES (
        'Sales DB', 'postgresql', 'psycopg2', 'db.example.com', 5432, 'sales_user', 'supersecret', 'sales_prod', 'prod', 'require', 'admin', 'Main production database for sales data'
    );
    """)
    
    cursor.execute("""
    INSERT INTO db_connections (
        name, dialect, driver, host, port, username, password, database_name, environment, ssl_mode, created_by, description
    ) VALUES (
        'Dev Analytics', 'mysql', 'pymysql', '127.0.0.1', 3306, 'dev_user', 'devpass123', 'analytics_dev', 'dev', NULL, 'developer', 'Local development database for analytics testing'
    );
    """)

    # -------------------------
    # COMMIT & CLOSE
    # -------------------------

    conn.commit()
    conn.close()

    print(f"Database '{db_path}' created with sample data.")


if __name__ == "__main__":
    create_database()