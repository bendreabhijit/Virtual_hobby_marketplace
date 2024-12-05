from pydantic import BaseModel

class HobbyBase(BaseModel):
    name: str
    description: str
    price: float

class HobbyCreate(HobbyBase):
    user_id: int

class HobbyResponse(HobbyBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True  # Updated for Pydantic v2
