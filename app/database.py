from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

#create SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True) #Create a connection to the database

#Create a session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #A factory that creates database session objects, which are used to interact with the database.

#Create a base class
Base = declarative_base() #Defining database models

#Dependency to get database session
def get_db():
    db = SessionLocal() #Create a new session
    try:
        yield db #Provide it to the request
    finally:
        db.close() #Close the session after the request is finished