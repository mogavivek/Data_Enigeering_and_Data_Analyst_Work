# =========================================================
# PROJECT ETL PIPELINE
# =========================================================

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
import pandas as pd
import requests

# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(title="ProjectETL Pipeline")

# =========================================================
# DATABASE CONFIGURATION
# =========================================================

engine = create_engine(
    "sqlite:///analytics.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# =========================================================
# DATABASE MODEL
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String)
    email = Column(String)
    city = Column(String)

# Create table
Base.metadata.create_all(bind=engine)

# =========================================================
# PYDANTIC RESPONSE MODEL
# =========================================================

class UserResponse(BaseModel):

    id: int
    name: str
    username: str
    email: str
    city: str

    class Config:
        from_attributes = True

# =========================================================
# DATABASE SESSION
# =========================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# =========================================================
# ETL PIPELINE
# =========================================================

def run_etl():

    print("Starting ETL Pipeline...")

    # =====================================================
    # EXTRACT
    # =====================================================

    print("Extracting data...")

    url = "https://jsonplaceholder.typicode.com/users"

    response = requests.get(url)

    data = response.json()

    # Convert JSON -> Pandas DataFrame
    df = pd.DataFrame(data)

    print(df.head())

    # =====================================================
    # TRANSFORM
    # =====================================================

    print("Transforming data...")

    # Extract nested city field
    df["city"] = df["address"].apply(
        lambda x: x["city"]
    )

    # Keep only needed columns
    df = df[
        [
            "id",
            "name",
            "username",
            "email",
            "city"
        ]
    ]

    # Remove duplicate emails
    df.drop_duplicates(
        subset=["email"],
        inplace=True
    )

    # Standardize names
    df["name"] = df["name"].str.title()

    print(df.head())

    # =====================================================
    # LOAD
    # =====================================================

    print("Loading data into database...")

    db = SessionLocal()

    try:

        for _, row in df.iterrows():

            # Prevent duplicate users
            existing_user = db.query(User).filter(
                User.email == row["email"]
            ).first()

            if not existing_user:

                new_user = User(
                    id=int(row["id"]),
                    name=row["name"],
                    username=row["username"],
                    email=row["email"],
                    city=row["city"]
                )

                db.add(new_user)

        db.commit()

        print("ETL Completed Successfully!")

    finally:
        db.close()

# Run ETL automatically
run_etl()

# =========================================================
# API ENDPOINTS
# =========================================================

# Root Endpoint
@app.get("/")
def root():

    return {
        "message": "ProjectETL Pipeline Running"
    }

# Get all users
@app.get(
    "/users/",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):

    return db.query(User).all()

# Get single user
@app.get(
    "/users/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        return {
            "message": "User not found"
        }

    return user