from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth
from app.models.user import Base
from app.database import engine
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) 

logger = logging.getLogger(__name__)

try:
    Base.metadata.create_all(bind = engine)
    logger.info("Database tables created successfully")
except Exception as e :
    logger.error(f"Error creating database tables: {str(e)}")

app = FastAPI(
    title="Login API",
    description= "A RESTful API for user authentification",
    version="1.0.0"
)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:19000",  # For Expo
    "http://localhost:19001",  # For Expo
    "http://localhost:19002",  # For Expo
    # Add production domains here
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Welcome to the Login API"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)