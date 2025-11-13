from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from database import db
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from bson import ObjectId

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "gbrish"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# Use absolute token URL so OAuth dependencies resolve correctly regardless of router include style
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --------------------
# Pydantic models
# --------------------
class CreateUserRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --------------------
# Dependency
# --------------------
async def get_db():
    return db

db_dependency = Depends(get_db)

# --------------------
# Helper functions
# --------------------
async def authenticate_user(username: str, password: str, db):
    user = await db["users"].find_one({"username": username})
    if not user:
        return False
    if not bcrypt_context.verify(password, user["hashed_password"]):
        return False
    return user

def create_access_token(username: str, user_id: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user.")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user.")

# --------------------
# Routes
# --------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db = db_dependency):
    # Check if username already exists
    existing_user = await db["users"].find_one({"username": create_user_request.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password
    hashed_pw = bcrypt_context.hash(create_user_request.password)

    # Insert into MongoDB
    result = await db["users"].insert_one({
        "username": create_user_request.username,
        "hashed_password": hashed_pw
    })

    return {"user_id": str(result.inserted_id), "username": create_user_request.username}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db = db_dependency):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user.")
    
    token = create_access_token(user["username"], str(user["_id"]), timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
