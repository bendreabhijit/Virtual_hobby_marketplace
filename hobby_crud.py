
# # hobby_crud.py
# from sqlalchemy.orm import Session
# from hobby_model import Hobby

# # Create a new hobby
# def create_hobby(db: Session, name: str, description: str, price: float, user_id: int):
#     new_hobby = Hobby(name=name, description=description, price=price, user_id=user_id)
#     db.add(new_hobby)
#     db.commit()
#     db.refresh(new_hobby)
#     return new_hobby

# # Read all hobbies
# def get_hobbies(db: Session):
#     return db.query(Hobby).all()

# # Update a hobby
# def update_hobby(db: Session, hobby_id: int, name: str, description: str, price: float):
#     hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
#     if hobby:
#         hobby.name = name
#         hobby.description = description
#         hobby.price = price
#         db.commit()
#         db.refresh(hobby)
#     return hobby

# # Delete a hobby
# def delete_hobby(db: Session, hobby_id: int):
#     hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
#     if hobby:
#         db.delete(hobby)
#         db.commit()
#     return hobby
from sqlalchemy.orm import Session
from hobby_model import Hobby  # Your SQLAlchemy Hobby model
from hobby_post_model import HobbyCreate  # Import the Pydantic model

def create_hobby(db: Session, hobby: HobbyCreate):
    db_hobby = Hobby(**hobby.dict())
    db.add(db_hobby)
    db.commit()
    db.refresh(db_hobby)
    return db_hobby

def get_hobbies(db: Session):
    return db.query(Hobby).all()

def update_hobby(db: Session, hobby_id: int, name: str, description: str, price: float):
    hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if hobby:
        hobby.name = name
        hobby.description = description
        hobby.price = price
        db.commit()
        db.refresh(hobby)
    return hobby