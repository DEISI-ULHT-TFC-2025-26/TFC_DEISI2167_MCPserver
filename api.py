from fastapi import APIRouter, FastAPI, Request, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from crud import DB
import hashlib
import os
import secrets

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

# ==========================================
# SISTEMA DE SEGURANÇA
# ==========================================
security = HTTPBasic()

def verificar_admin(credentials: HTTPBasicCredentials = Depends(security)):
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "admin")

    correct_username = secrets.compare_digest(credentials.username, ADMIN_USER)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASS)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais incorretas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ==========================================
# REGISTO DA API
# ==========================================
def register_api(name: str, version: str, db: DB) -> FastAPI:
    """Register a FastAPI app with static files and routes."""
    
    templates = Jinja2Templates(directory="static")
    app = FastAPI()

    # AVISO DE SEGURANÇA NO ARRANQUE
    @app.on_event("startup")
    async def verificar_seguranca_inicial():
        import os
        #alerta se o utilizador não tiver passado a password no Docker
        if os.getenv("ADMIN_PASSWORD") is None:
            print("\n" + "⚠️ "*25)
            print(" AVISO DE SEGURANÇA: Nenhuma password definida no Docker! ")
            print(" O sistema está a usar as credenciais por defeito: admin / admin")
            print(" ")
            print(" Para proteger o sistema, pare o contentor e inicie novamente com a flag:")
            print(" -> -e ADMIN_PASSWORD=\"sua_password_segura\"")
            print("⚠️ "*25 + "\n")
    
    # Monta a pasta static
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Protege as rotas da API de uma só vez
    api_router = APIRouter(prefix="/api", dependencies=[Depends(verificar_admin)])

    # Rota da Página Inicial Protegida (exige username/password)
    @app.get("/")
    def home(request: Request, username: str = Depends(verificar_admin)):
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