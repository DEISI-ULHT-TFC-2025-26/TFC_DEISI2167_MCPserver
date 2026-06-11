from fastapi import APIRouter, FastAPI, Request, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from crud import DB
import hashlib

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
    try:
        with open('.admin_secret', 'r') as f:
            hash_guardado = f.read().strip()
    except FileNotFoundError:
        hash_guardado = hashlib.sha256(b"admin").hexdigest()

    hash_inserido = hashlib.sha256(credentials.password.encode()).hexdigest()

    if credentials.username != "admin" or hash_inserido != hash_guardado:
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
        if not os.path.exists('.admin_secret'):
            print("\n" + "⚠️ "*25)
            print(" AVISO DE SEGURANÇA: Password por defeito em uso! ")
            print(" O sistema está configurado com as credenciais: admin / admin")
            print(" ")
            print(" Para proteger o sistema, abra outro terminal e corra:")
            print(" -> python set_password.py ou python3 set_password.py")
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