


from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from Vdatabase import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from Vdatabase import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(255), default="buyer", nullable= False)  #default to buyer to new user 
   
    hobbies = relationship("Hobby", back_populates="user")


