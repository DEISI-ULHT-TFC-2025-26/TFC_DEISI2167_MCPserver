#Segurança da Porta - rotas REST, ConnectionModel

from fastapi import APIRouter, FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from crud import DB

# 1. Definir o Modelo de Dados esperado pelo formulário (Pydantic)
class ConnectionModel(BaseModel):
    name: str
    dialect: str
    driver: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: str
    description: Optional[str] = None

# Alteramos a assinatura para receber a instância da base de dados (db)
def register_api(name: str, version: str, db: DB) -> FastAPI:
    """Register a FastAPI app with static files and routes."""
    
    templates = Jinja2Templates(directory="static")
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="static"), name="static")

    api_router = APIRouter(prefix="/api")

    @app.get("/")
    def home(request: Request):
        return templates.TemplateResponse(request, "index.html")

    @api_router.get("/version")
    def version_route():
        return {"name": name, "version": version}

    @api_router.get("/health")
    def health():
        return {"status": "ok"}

    # ==========================================
    # REST API PARA AS CONEXÕES (CRUD)
    # ==========================================

    @api_router.get("/connections")
    def get_connections():
        return db.get_all("db_connections")

    @api_router.post("/connections")
    def create_connection(conn: ConnectionModel):
        try:
            # Convert model to dict
            data = conn.model_dump(exclude_unset=True)
            new_id = db.insert("db_connections", data)
            return {"message": "Conexão criada", "id": new_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @api_router.put("/connections/{conn_id}")
    def update_connection(conn_id: int, conn: ConnectionModel):
        try:
            data = conn.model_dump(exclude_unset=True)
            db.update("db_connections", conn_id, data)
            return {"message": "Conexão atualizada", "id": conn_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @api_router.delete("/connections/{conn_id}")
    def delete_connection(conn_id: int):
        try:
            db.delete("db_connections", conn_id)
            return {"message": "Conexão eliminada", "id": conn_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(api_router)
    return app