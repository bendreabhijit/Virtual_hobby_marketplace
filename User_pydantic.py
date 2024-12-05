from pydantic import BaseModel, Field
from typing import List
from hobby_post_model import HobbyBase, HobbyResponse

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role:str
    

class UserOut(UserBase):
    id: int
    role:str
    hobbies: List[HobbyResponse] = []

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


    class Config:
        # orm_mode = True
         from_attributes = True

