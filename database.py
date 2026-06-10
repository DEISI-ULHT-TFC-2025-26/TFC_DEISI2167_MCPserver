from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, declarative_base

 

# SQLite database path (will be stored inside /app/data)

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/app.db"

 

# Create engine

engine = create_engine(

    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}

)

 

# Create session factory

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

 

# Base class for models

Base = declarative_base()

 

# Dependency to get DB session per request

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()