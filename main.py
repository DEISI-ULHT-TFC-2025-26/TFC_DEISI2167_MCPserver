from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, text
import os

DATABASE_URL = "mssql+pymssql://sa:Password_123!@host.docker.internal:1433/DW"
engine = create_engine(DATABASE_URL)

mcp = FastMCP("DataWarehouseServer")

@mcp.tool()
def listar_tabelas() -> str:
    """Lista todas as tabelas no formato 'schema.tabela' para que possas consultar corretamente."""
    query = """
    SELECT s.name + '.' + t.name
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            tabelas = [row[0] for row in result]
            return f"Tabelas disponíveis (Usa sempre o nome completo): {', '.join(tabelas)}"
    except Exception as e:
        return f"Erro ao listar tabelas: {str(e)}"

@mcp.tool()
def executar_query_sql(query: str) -> str:
    """Executa uma consulta SQL (SELECT) na base de dados."""
    if not query.strip().upper().startswith("SELECT"):
        return "Erro de Segurança: Apenas SELECT é permitido."
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            linhas = result.fetchall()
            return str([dict(row._mapping) for row in linhas])
    except Exception as e:
        return f"Erro ao executar query: {str(e)}"
    

"""@mcp.tool()
def listar_schemas() -> str:
    Lista todos os schemas disponíveis na base de dados para entender a organização das tabelas.
    # Filtramos esquemas de sistema para não confundir o LLM
    query =
    SELECT name 
    FROM sys.schemas 
    WHERE name NOT IN ('sys', 'information_schema', 'guest', 'db_owner', 'db_accessadmin')
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            schemas = [row[0] for row in result]
            return f"Schemas encontrados: {', '.join(schemas)}"
    except Exception as e:
        return f"Erro ao listar schemas: {str(e)}" """


if __name__ == "__main__":
    import uvicorn

    app = mcp.sse_app()
    uvicorn.run(app, host="0.0.0.0", port=8080)