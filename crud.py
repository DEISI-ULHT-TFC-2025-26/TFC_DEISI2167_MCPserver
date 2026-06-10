#Segurança da Porta - rotas REST, ConnectionModel

import sqlite3
from typing import Any, Dict, List, Optional


class DB:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # return dict-like rows
        return conn

    # -------------------------
    # CREATE
    # -------------------------
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())

        query = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"

        with self._connect() as conn:
            cursor = conn.execute(query, values)
            conn.commit()
            return cursor.lastrowid

    # -------------------------
    # READ
    # -------------------------
    def get_all(self, table: str) -> List[Dict]:
        query = f"SELECT * FROM {table}"

        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(row) for row in rows]

    def get_by_id(self, table: str, id_value: Any, id_column: str = "id") -> Optional[Dict]:
        
        query = f"SELECT * FROM {table} WHERE {id_column} = ?"

        with self._connect() as conn:
            row = conn.execute(query, (id_value,)).fetchone()
            return dict(row) if row else None

    def filter(self, table: str, conditions: Dict[str, Any]) -> List[Dict]:
        where_clause = " AND ".join([f"{k} = ?" for k in conditions])
        values = list(conditions.values())

        query = f"SELECT * FROM {table} WHERE {where_clause}"

        with self._connect() as conn:
            rows = conn.execute(query, values).fetchall()
            return [dict(row) for row in rows]

    def get_url_by_id(self, table: str, id_value: Any, id_column: str = "id") -> Optional[Dict]:
            
        row = self.get_by_id(table, id_value, id_column)
                 
        db_type = row["dialect"]
        driver = row["driver"]
        username = row["username"]
        password = row["password"]
        host = row["host"]
        port = row["port"]
        database = row["database_name"]

        # Construct SQLAlchemy URL
        if driver:
            return f"{db_type}+{driver}://{username}:{password}@{host}:{port}/{database}"
        else:
            return f"{db_type}://{username}:{password}@{host}:{port}/{database}"
        
    # -------------------------
    # UPDATE
    # -------------------------
    def update(
        self,
        table: str,
        id_value: Any,
        data: Dict[str, Any],
        id_column: str = "id"
    ) -> int:
        set_clause = ", ".join([f"{k} = ?" for k in data])
        values = list(data.values())
        values.append(id_value)

        query = f"UPDATE {table} SET {set_clause} WHERE {id_column} = ?"

        with self._connect() as conn:
            cursor = conn.execute(query, values)
            conn.commit()
            return cursor.rowcount

    # -------------------------
    # DELETE
    # -------------------------
    def delete(self, table: str, id_value: Any, id_column: str = "id") -> int:
        query = f"DELETE FROM {table} WHERE {id_column} = ?"

        with self._connect() as conn:
            cursor = conn.execute(query, (id_value,))
            conn.commit()
            return cursor.rowcount