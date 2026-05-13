from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Integration with SQL - code with Josh")

engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread": False}) # just creating the users.db file
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# database Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(100), nullable=False)
    

Base.metadata.create_all(engine)

# Pydantic Models (Dataclass)
class UserCreate(BaseModel):
    name:Optional[str]=None
    email:Optional[str]=None
    role:Optional[str]=None
    
# the below class is for safety side
class UserResponse(BaseModel):
    id: int
    name:str
    email:str
    role:str
    
    class Confing:
        from_attributes=True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
get_db()


# Endpoints
@app.get("/")
def root():
    return {"message": "Intro to FastAPI with SQL - Code with ease"}

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id:int, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

# add the user
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db:Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="User already exists!")
    
    # Otherwise create a new user
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
    

# update the user
@app.update("/user/{user_id}", response_model=UserResponse)
def update_user(user_id:int, user: UserCreate, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exists!")
    
    # Only update the provided fields
    update_data = user.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Delete user
@app.delete("/user/{user_id}", response_model=UserResponse)
def delete_user(user_id:int, user: UserCreate, db:Session=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exists!")
    
    db.delete(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Get all the user
@app.get("/users/", response_model=List(UserResponse))
def get_all_users(db:Session=Depends(get_db)):
    return db.query(User).all()