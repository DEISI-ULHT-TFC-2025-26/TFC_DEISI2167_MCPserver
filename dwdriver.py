# Operário dos Dados - DWConnection

from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
from urllib.parse import urlparse, urlunparse
import os
import csv
from sqlalchemy import select, table, column
import json
import openpyxl

class DWConnection:
    """
    A class to connect to multiple database types and inspect table metadata.
    """

    def __init__(self, db_url: str):
        """
        Initialize with SQLAlchemy database URL.
        Examples of db_url:
        - PostgreSQL: postgresql+psycopg2://user:password@host:port/dbname
        - MySQL: mysql+pymysql://user:password@host:port/dbname
        - SQLite: sqlite:///path/to/db.sqlite
        """
        self.db_url = db_url
        self.engine: Engine = None
        self.metadata: MetaData = None
    

    def _mask_db_url(self, db_url: str) -> str:
        parsed = urlparse(db_url)
            
        if parsed.password:
            netloc = parsed.netloc.replace(parsed.password, "*" * len(parsed.password))
        else:
            netloc = parsed.netloc
        return urlunparse(parsed._replace(netloc=netloc))


    def connect(self):
        """Create engine and initialize metadata."""
        try:
            self.engine = create_engine(self.db_url)
            self.metadata = MetaData()
            print(f"Connected to database: {self._mask_db_url(self.db_url)}")
        except SQLAlchemyError as e:
            print(f"Error connecting to database: {e}")
            raise
        

    def list_schemas(self):
        """Return a list of all schemas in the database."""
        self.connect()
        try:
            inspector = inspect(self.engine)
            schemas = inspector.get_schema_names()
            schemas = [s for s in schemas if s.lower() not in ["sys", "information_schema"]]
            return schemas
        except SQLAlchemyError as e:
            print(f"Error fetching schemas: {e}")
            return []


    def list_tables(self):
        """Return a list of table names including schema: schema.table"""
        self.connect()  # make sure engine exists
        all_tables = []
        try:
            inspector = inspect(self.engine)
            schemas = inspector.get_schema_names()
            for schema in schemas:
                tables = inspector.get_table_names(schema=schema)
                all_tables.extend([f"{schema}.{table}" for table in tables])
            return all_tables
        except SQLAlchemyError as e:
            print(f"Error fetching tables: {e}")
            return []


    def list_table_metadata(self, table_name: str = None):
        """
        Return metadata of a specific table as a dict:
        {column_name: column_type}
        """
        self.connect()  # ensure engine exists

        if "." in table_name:
            schema, table_name = table_name.split(".", 1)  # split at first dot only
        else:
            schema = "dbo"           # default schema if missing
        try:
            inspector = inspect(self.engine)
            if schema != None and table_name is not None:
                columns = inspector.get_columns(table_name, schema=schema)
            else:
                columns = inspector.get_columns(table_name)
            return {col['name']: str(col['type']) for col in columns}
        except SQLAlchemyError as e:
            print(f"Error fetching metadata for table {schema}.{table_name}: {e}")
            return {}
        

    def list_all_tables_metadata(self):
        """
        Return metadata for all tables in all schemas:
        {
            "schema.table_name": {
                "columns": {
                    "column_name": {
                        "type": str,
                        "nullable": bool,
                        "default": str,
                        "primary_key": bool
                    }
                }
            }
        }
        """
        self.connect()
        all_metadata = {}
        try:
            inspector = inspect(self.engine)
            schemas = inspector.get_schema_names()
            for schema in schemas:
                # Skip system schemas for SQL Server
                if schema.lower() in ["sys", "information_schema"]:
                    continue

                tables = inspector.get_table_names(schema=schema)
                for table in tables:
                    full_table_name = f"{schema}.{table}"
                    columns = inspector.get_columns(table, schema=schema)
                    table_metadata = {}
                    for col in columns:
                        table_metadata[col["name"]] = {
                            "type": str(col["type"]),
                            "nullable": col["nullable"],
                            "default": col["default"],
                            "primary_key": col.get("primary_key", False)
                        }
                    all_metadata[full_table_name] = {"columns": table_metadata}

            return all_metadata

        except SQLAlchemyError as e:
            print(f"Error fetching tables metadata: {e}")
            return {}


    def list_fact_tables(self):
        fact_tables = self.list_tables()
        return [ t for t in fact_tables if t.lower().split('.')[-1].startswith(('f_', 'fact_'))]  # Filter tables that start with "Fact_"


    def list_dimension_tables(self):
        dimension_tables = self.list_tables() 
        return [t for t in dimension_tables if t.lower().split('.')[-1].startswith(("dim_", "d_"))]  # Filter tables that start with "Dim_" or "D_"


    def execute_query(self, query: str) -> str:
        if not query.strip().upper().startswith("SELECT"):
           return "Erro de Segurança: Apenas SELECT é permitido."
        self.connect()
        try:
            with self.engine.connect() as conn:

                result = conn.execute(text(query))
                linhas = result.fetchall()
                return str([dict(row._mapping) for row in linhas])
        except Exception as e:
            return f"Erro ao executar query: {str(e)}"
        

    def get_column_unique_values(self, table_name: str, column_name: str):
        """Devolve até 50 valores únicos de uma coluna."""
        self.connect()
        
        if "." in table_name:
            schema, t_name = table_name.split(".", 1)
        else:
            schema = "dbo"
            t_name = table_name

        try:
            tbl = table(t_name, column(column_name), schema=schema)
            stmt = select(tbl.c[column_name]).distinct().limit(50)
            
            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                valores = [str(row[0]) for row in result if row[0] is not None]
                return valores
        except Exception as e:
            return f"Erro ao obter valores únicos: {str(e)}"


    def get_table_relationships(self, table_name: str):
        """Descobre as chaves estrangeiras (Foreign Keys) de uma tabela."""
        self.connect()
        
        if "." in table_name:
            schema, t_name = table_name.split(".", 1)
        else:
            schema = "dbo"
            t_name = table_name

        try:
            inspector = inspect(self.engine)
            fks = inspector.get_foreign_keys(t_name, schema=schema)
            
            if not fks:
                return f"A tabela {table_name} não tem chaves estrangeiras declaradas."
                
            relationships = []
            for fk in fks:
                rel = (f"As colunas {fk['constrained_columns']} "
                       f"apontam para {fk['referred_schema']}.{fk['referred_table']} "
                       f"nas colunas {fk['referred_columns']}.")
                relationships.append(rel)
            return relationships
        except Exception as e:
            return f"Erro ao inspecionar relações: {str(e)}"


    def export_query_to_csv(self, query: str, filename: str) -> str:
        """Executa a query e exporta para a pasta static/exports"""
        query_upper = query.strip().upper()
        if not (query_upper.startswith("SELECT") or query_upper.startswith("WITH")):
            return "Erro de Segurança: Apenas SELECT ou WITH são permitidos."
            
        self.connect()
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                linhas = result.fetchall()
                
                if not linhas:
                    return "A query não retornou dados para exportar."

                # Garantir que a pasta existe
                export_dir = os.path.join("static", "exports")
                os.makedirs(export_dir, exist_ok=True)

                if not filename.endswith(".csv"):
                    filename += ".csv"
                filepath = os.path.join(export_dir, filename)

                with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(result.keys())
                    for row in linhas:
                        writer.writerow(row)

                return f"Sucesso! Os dados foram guardados no ficheiro {filename}. URL para download: http://127.0.0.1:9991/static/exports/{filename}"
        except Exception as e:
            return f"Erro ao exportar CSV: {str(e)}"
        

    def export_query_to_json(self, query: str, filename: str) -> str:
        """Executa a query e exporta para a pasta static/exports em formato JSON"""
        query_upper = query.strip().upper()
        if not (query_upper.startswith("SELECT") or query_upper.startswith("WITH")):
            return "Erro de Segurança: Apenas SELECT ou WITH são permitidos."
            
        self.connect()
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                linhas = result.fetchall()
                
                if not linhas:
                    return "A query não retornou dados para exportar."

                export_dir = os.path.join("static", "exports")
                os.makedirs(export_dir, exist_ok=True)

                if not filename.endswith(".json"):
                    filename += ".json"
                filepath = os.path.join(export_dir, filename)

                dados = [dict(zip(result.keys(), row)) for row in linhas]

                with open(filepath, mode='w', encoding='utf-8') as f:
                    json.dump(dados, f, indent=4, default=str)

                return f"Sucesso! Os dados foram guardados no ficheiro {filename}. URL para download: http://127.0.0.1:9991/static/exports/{filename}"
        except Exception as e:
            return f"Erro ao exportar JSON: {str(e)}"
        

    def export_query_to_excel(self, query: str, filename: str) -> str:
        """Executa a query e exporta para a pasta static/exports em formato Excel (.xlsx)"""
        query_upper = query.strip().upper()
        if not (query_upper.startswith("SELECT") or query_upper.startswith("WITH")):
            return "Erro de Segurança: Apenas SELECT ou WITH são permitidos."
            
        self.connect()
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                linhas = result.fetchall()
                
                if not linhas:
                    return "A query não retornou dados para exportar."

                export_dir = os.path.join("static", "exports")
                os.makedirs(export_dir, exist_ok=True)

                if not filename.endswith(".xlsx"):
                    filename += ".xlsx"
                filepath = os.path.join(export_dir, filename)

                # Criar o ficheiro Excel
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Exportação de Dados"

                ws.append(list(result.keys()))

                for row in linhas:
                    linha_limpa = [str(val) if val is not None else "" for val in row]
                    ws.append(linha_limpa)

                wb.save(filepath)

                return f"Sucesso! Os dados foram guardados no ficheiro {filename}. URL para download: http://127.0.0.1:9991/static/exports/{filename}"
        except Exception as e:
            return f"Erro ao exportar Excel: {str(e)}"
    


