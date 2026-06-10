#DB

from api import register_api
from fastmcp import FastMCP
import asyncio
import uvicorn

MCP_NAME = "DWMCPServer"
VERSION = "v.1.0.0"

# =========================================================
# DB SERVER
# =========================================================
from crud import DB

db = DB("db/mcp.db")


# =========================================================
# MCP SERVER
# =========================================================
from tools.mcp import register_mcp_tools

mcp = FastMCP(name=MCP_NAME,  # Name of your MCP server
              version=VERSION        # Optional: version info
            )

register_mcp_tools(mcp, db)


# =========================================================
# FASTAPI
# =========================================================
from api import register_api

app = register_api(MCP_NAME, VERSION, db)  # Pass the DB instance to the API registration function


# =========================================================
# RUN BOTH CLEANLY
# =========================================================

async def run_mcp():
    await mcp.run_async( transport="http", host="0.0.0.0", port=9990 )


async def run_fastapi():
    config = uvicorn.Config( app, host="0.0.0.0", port=9991, log_level="info" )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        run_fastapi(),
        run_mcp()
    )

if __name__ == "__main__":
    asyncio.run(main())