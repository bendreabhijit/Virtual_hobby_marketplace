# hobby_model.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from Vdatabase import Base
# class Hobby(Base):
#     __tablename__ = "hobbies"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50), nullable=False, index=True)
#     description = Column(String(50), nullable=False, index=True)
#     price = Column(Float, nullable=False, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'))  # Foreign key referencing users

#     # Forward reference to "User" class
#     user = relationship("User", back_populates="hobbies")



 
class Hobby(Base):
    __tablename__ = "hobbies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    description = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="hobbies")

