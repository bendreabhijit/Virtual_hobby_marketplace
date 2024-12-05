from fastapi import HTTPException
from sqlalchemy.orm import Session
from Vmodel import User
from User_pydantic import UserCreate
from bcrypt import hashpw, gensalt
from sqlalchemy.orm import Session
from hobby_model import Hobby
from main import verify_password
from passlib.context import CryptContext
 
 

def authenticate_user(db: Session, username: str, password: str):
    # Query the user by username
    user = db.query(User).filter(User.username == username ).first()
    
    # If user is found, verify the password
    
    if user and verify_password(password, user.hashed_password):
        return user  # Return the user if authentication is successful
    
    return False  # Return False if authentication fails

def hash_password(password: str) -> str:
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

# def create_user(db: Session, user: UserCreate):
#     role = user.role if user.role else "buyer"
#     db_user = User(username=user.username, email=user.email, hashed_password=user.password, role=role)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
 
import logging
def create_user(db : Session, user: UserCreate):
    role = user.role if user.role else "buyer"
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logging.info(f"User created with role: {new_user.role}")
    return new_user




# def hash_password(password: str) -> str:
#     return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

# def create_user(db: Session, user: UserCreate):
#     hashed_password = hash_password(user["hashed_password"])
#     db_user = User(
#         username=user["username"],
#         email=user["email"],
#         password=hashed_password
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_name(db: Session, user_name: str):
    return db.query(User).filter(User.username == user_name).first()

def update_user_by_name(db: Session, user_name: str, email: str = None, password: str = None):
    db_user = db.query(User).filter(User.username == user_name).first()
    if db_user:
        if email:
            db_user.email = email
        if password:
            db_user.password = hash_password(password)
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_user_by_id(db: Session, user_id: int, username: str = None, email: str = None, password: str = None):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        if username:
            db_user.username = username
        if email:
            db_user.email = email
        if password:
            db_user.password = hash_password(password)
        db.commit()
        db.refresh(db_user)
        return {"message": f"User '{username}' updated successfully"}
    return None

def delete_user_by_name(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
        return {"message": f"User '{username}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
