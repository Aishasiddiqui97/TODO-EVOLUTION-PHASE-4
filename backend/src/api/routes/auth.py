from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict
from ...models.user import User
from ...db import get_session
from ...auth.jwt import create_access_token
from pydantic import BaseModel

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

import uuid

# ... imports ...

@router.post("/auth/login", response_model=TokenResponse)
def login(user_login: UserLogin, session: Session = Depends(get_session)):
    # In a real app, you would verify the user's credentials against the database
    # For this demo, we'll simulate successful authentication
    # and return a JWT token

    # This is where you would typically:
    # 1. Look up the user by email in the database
    # 2. Verify the password using a hashing function
    # 3. If valid, create and return a JWT token

    # For demo purposes, we'll generate a consistent UUID for the demo user
    # In a real app this would come from the database
    demo_user_id = "550e8400-e29b-41d4-a716-446655440000" 
    user_data = {"user_id": demo_user_id, "email": user_login.email}
    token = create_access_token(data=user_data)

    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/register", response_model=TokenResponse)
def register(user_register: UserRegister, session: Session = Depends(get_session)):
    # In a real app, you would:
    # 1. Check if user already exists
    # 2. Hash the password
    # 3. Create a new user in the database
    # 4. Return a JWT token

    # For demo purposes, create a new random UUID
    user_id = str(uuid.uuid4())
    user_data = {"user_id": user_id, "email": user_register.email}
    token = create_access_token(data=user_data)

    return {"access_token": token, "token_type": "bearer"}