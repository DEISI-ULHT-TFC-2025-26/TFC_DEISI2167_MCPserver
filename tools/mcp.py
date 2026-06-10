# tools/mcp.py
import mcp

from dwdriver import DWConnection
from fastmcp import FastMCP
from crud import DB

dw = None

def register_mcp_tools(mcp: FastMCP, db: DB):

    db_url = db.get_url_by_id("db_connections", 1)  # Get the URL for the first connection
    global dw
    dw = DWConnection(db_url)
        
    @mcp.tool(description="Returns the current version of the MCP server.")
    def version() -> str:
        return f"{mcp.name} {mcp.version}"

    @mcp.tool(description="Retrieves all DW connections that the MCP is able to connect to.")
    def get_connections():
        return db.get_all("db_connections")
    
    @mcp.tool(description="Connect to a specific DW.")
    def dw_connect(id: int = 1):
        db_url = db.get_url_by_id("db_connections", id )  # Get the URL for the first connection
        global dw
        dw = DWConnection(db_url)
        return f"Now connected to DW with ID {id}"

    @mcp.tool(description="Retrieves all schemas in the DW.")
    def list_schemas():
        global dw
        return dw.list_schemas()

    @mcp.tool(description="Retrieves all tables in the DW.")
    def list_tables():
        global dw
        return dw.list_tables()
    
    @mcp.tool(description="Retrieves metadata for a specific table in the DW.")
    def list_table_metadata(table_name: str = None):
        global dw
        return dw.list_table_metadata(table_name)
        
    @mcp.tool(description="Retrieves metadata for all tables in the DW.")
    def list_all_tables_metadata():
        global dw
        return dw.list_all_tables_metadata()
    
    @mcp.tool(description="Execute a SQL query (only SELECT allowed) against the connected DW and return results.")
    def execute_query(query: str) -> str:
        global dw
        return dw.execute_query(query)
    
    @mcp.tool(description="List all fact tables names in the DW (tables that start with 'Fact_' or 'F_').")
    def list_fact_tables():
        global dw
        return dw.list_fact_tables()
    
    @mcp.tool(description="List all dimension tables names in the DW (tables that start with 'Dim_' or 'D_').")
    def list_dimension_tables():
        global dw
        return dw.list_dimension_tables()
    
    @mcp.tool(description="Gets up to 50 unique values from a specific column in a table. Useful to understand data formats or categorical values.")
    def get_column_unique_values(table_name: str, column_name: str):
        global dw
        return dw.get_column_unique_values(table_name, column_name)

    @mcp.tool(description="Retrieves the foreign keys and relationships of a table, showing how it connects to other dimensions or fact tables.")
    def get_table_relationships(table_name: str):
        global dw
        return dw.get_table_relationships(table_name)

    @mcp.tool(description="Executes a SELECT query and exports the results to a CSV file. Returns the URL to download the file.")
    def export_query_to_csv(query: str, filename: str) -> str:
        global dw
        return dw.export_query_to_csv(query, filename)

    # Dicionário para o glossário
    BUSINESS_GLOSSARY = {
        "YTD Revenue": "Soma de SalesAmount para o ano atual.",
        "Active Customer": "Cliente com pelo menos uma compra registada nos últimos 12 meses.",
        "Churn Rate": "Percentagem de clientes que não efetuaram compras no último trimestre.",
        "Net Profit": "Revenue total menos o custo (Total Cost)."
    }

    @mcp.tool(description="Searches the business glossary for definitions of business terms, acronyms, or metrics.")
    def get_business_glossary(term: str) -> str:
        for key, definition in BUSINESS_GLOSSARY.items():
            if term.lower() in key.lower():
                return f"Termo: {key} -> Definição de negócio: {definition}"
        return "Termo não encontrado no glossário. Podes ter de deduzir a fórmula com base nas tabelas."
    
