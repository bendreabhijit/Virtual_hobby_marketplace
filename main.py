from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from Vdatabase import SessionLocal, engine, Base
from hobby_model import Hobby
from Vmodel import User
from hobby_post_model import HobbyCreate, HobbyResponse
from User_pydantic import UserOut, UserCreate, UserLogin, Token
import hobby_crud
import Vcrud
from typing import List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import timedelta, datetime
import logging

app = FastAPI()
router = APIRouter()
Base.metadata.create_all(bind=engine)

# Dependency for creating and closing a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT configurations
SECRET_KEY = "MansiNibe"  # Change this to a secure key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT utility functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user

def create_access_token(username: str, user_role: str, expires_delta: timedelta = None):
    to_encode = {"username": username, "role": user_role}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        role: str = payload.get("role")
        user_id: int = payload.get("user_id")  # Ensure user_id is retrieved here

        if username is None or role is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    return {"username": username, "role": role, "id": user_id}

def require_role(allowed_roles: List[str]):
    async def role_dependency(user: dict = Depends(get_current_user)):
        user_role = user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required role to access this resource",
            )
    return role_dependency

# User Endpoints
@app.post("/add_user/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user.password = get_password_hash(user.password)  # Hash the password
    return Vcrud.create_user(db=db, user=user)

@app.post("/token", response_model=dict)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = Vcrud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(username=user.username, user_role=user.role, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/get_all_users", response_model=List[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/get_user_by_id/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = Vcrud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/update_user_by_id/{user_id}", response_model=UserOut, dependencies=[Depends(require_role("admin"))])
def update_user_by_id(user_id: int, username: str = None, email: str = None, password: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return Vcrud.update_user_by_id(db, user_id, username, email, password)

@app.delete("/delete_user_by_name/{user_name}", dependencies=[Depends(require_role("admin"))])
def delete_user_by_name(user_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return Vcrud.delete_user_by_name(db, user_name)

### Hobby Endpoints
@app.get("/get_all_hobbies/", response_model=List[HobbyResponse])
async def get_hobbies(db: Session = Depends(get_db)):
    return hobby_crud.get_hobbies(db)

@app.post("/add_hobbies", dependencies=[Depends(require_role(["admin", "seller"]))])
async def add_hobbies(hobby: HobbyCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_hobby = Hobby(name=hobby.name, description=hobby.description, price=hobby.price, user_id=user['id'])
    db.add(db_hobby)
    db.commit()
    db.refresh(db_hobby)
    return {"message": "Hobby added successfully", "Hobby": db_hobby}

@app.put("/update_hobby/{hobby_id}", dependencies=[Depends(require_role("seller"))])
async def update_hobby(hobby_id: int, hobby: HobbyCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if db_hobby is None:
        raise HTTPException(status_code=404, detail="Hobby not found")
    
    # Check if the current user is the owner of the hobby
    if db_hobby.user_id != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to update this hobby")
    
    db_hobby.name = hobby.name
    db_hobby.description = hobby.description
    db_hobby.price = hobby.price
    
    db.commit()
    db.refresh(db_hobby)
    return {"message": "Hobby updated successfully", "Hobby": db_hobby}

@app.delete("/delete_hobby/{hobby_id}", dependencies=[Depends(require_role("seller"))])
async def delete_hobby(hobby_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if db_hobby is None:
        raise HTTPException(status_code=404, detail="Hobby not found")
    
    # Check if the current user is the owner of the hobby
    if db_hobby.user_id != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to delete this hobby")
    
    db.delete(db_hobby)
    db.commit()
    return {"message": "Hobby deleted successfully", "hobby": db_hobby}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
