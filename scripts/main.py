import socket
import json
from fastapi import FastAPI, Depends, HTTPException, Security, Request, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from scripts.database import get_db, init_db, UserModel, ClientModel, hash_password, verify_password
from scripts.logger import logger

app = FastAPI(
    title="ClientValueKey API",
    description="Web service for secure user and password management.",
    version="1.0.0",
    docs_url=None,  
    redoc_url=None
)

API_KEY_HEADER = APIKeyHeader(name="X-API-KEY", auto_error=False)
HOST_NAME = socket.gethostname()

init_db()

class UserCreate(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    mobile_number: str
    language: str
    culture: str
    password: str

class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    mobile_number: str | None = None
    language: str | None = None
    culture: str | None = None

class PasswordValidate(BaseModel):
    username: str
    password: str

async def verify_api_key_and_log(request: Request, db: Session = Depends(get_db), api_key: str = Security(API_KEY_HEADER)):
    client_ip = request.client.host
    method_name = f"{request.method} {request.url.path}"
    
    body_bytes = await request.body()
    req_params = {}
    if body_bytes:
        try:
            req_params = json.loads(body_bytes.decode('utf-8'))
            if "password" in req_params:
                req_params["password"] = "********"
        except Exception:
            req_params = {"error": "Invalid JSON"}
    
    client = db.query(ClientModel).filter(ClientModel.api_key == api_key).first() if api_key else None
    client_name = client.client_name if client else "Unknown Client"

    log_base = f"{client_ip} | {client_name} | {HOST_NAME} | {method_name} | Params: {json.dumps(req_params)}"
    
    if not client:
        logger.error(f"{log_base} | Message: Unauthorized access. API key: {api_key}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key.")

    request.state.log_base = log_base
    request.state.client_name = client_name
    return client

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
    )

@app.post("/users", status_code=201, dependencies=[Depends(verify_api_key_and_log)])
def create_user(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    # 1. Existing check for Username duplication
    if db.query(UserModel).filter(UserModel.username == user_data.username).first():
        logger.error(f"{request.state.log_base} | Message: Username already exists.")
        raise HTTPException(status_code=400, detail="Username is already taken.")

    # 2. ADDED: Check for Email duplication
    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        logger.error(f"{request.state.log_base} | Message: Email already exists.")
        raise HTTPException(status_code=400, detail="Email is already registered.")

    new_user = UserModel(
        username=user_data.username,
        full_name=user_data.full_name,
        email=user_data.email,
        mobile_number=user_data.mobile_number,
        language=user_data.language,
        culture=user_data.culture,
        password_hash=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"{request.state.log_base} | Message: User successfully created. ID: {new_user.id}")
    return {"id": new_user.id, "username": new_user.username, "status": "Created"}

@app.get("/users/{user_id}", dependencies=[Depends(verify_api_key_and_log)])
def get_user(user_id: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        logger.error(f"{request.state.log_base} | Message: User with ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found.")
    
    logger.info(f"{request.state.log_base} | Message: Successfully retrieved data for user {user.username}")
    return {
        "id": user.id, "username": user.username, "full_name": user.full_name,
        "email": user.email, "mobile_number": user.mobile_number,
        "language": user.language, "culture": user.culture
    }

@app.put("/users/{user_id}", dependencies=[Depends(verify_api_key_and_log)])
def update_user(user_id: str, update_data: UserUpdate, request: Request, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        logger.error(f"{request.state.log_base} | Message: User for update not found.")
        raise HTTPException(status_code=404, detail="User not found.")
    
    # 3. ADDED: If email is being updated, verify it does not conflict with another user
    if update_data.email and update_data.email != user.email:
        if db.query(UserModel).filter(UserModel.email == update_data.email).first():
            logger.error(f"{request.state.log_base} | Message: Update failed. Email already exists.")
            raise HTTPException(status_code=400, detail="Email is already registered.")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
        
    db.commit()
    logger.info(f"{request.state.log_base} | Message: User {user.username} successfully updated.")
    return {"status": "Updated"}

@app.delete("/users/{user_id}", dependencies=[Depends(verify_api_key_and_log)])
def delete_user(user_id: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        logger.error(f"{request.state.log_base} | Message: User for deletion not found.")
        raise HTTPException(status_code=404, detail="User not found.")
    
    db.delete(user)
    db.commit()
    logger.info(f"{request.state.log_base} | Message: User with ID {user_id} deleted.")
    return {"status": "Deleted"}

@app.post("/users/validate-password", dependencies=[Depends(verify_api_key_and_log)])
def validate_password(data: PasswordValidate, request: Request, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        logger.error(f"{request.state.log_base} | Message: Password validation failed for user {data.username}")
        return {"valid": False}
    
    logger.info(f"{request.state.log_base} | Message: Password validation successful for user {data.username}")
    return {"valid": True}

