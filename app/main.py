from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, users

#create database tables
Base.metadata.create_all(bind = engine)

app = FastAPI(
    title="User Registration API",
    description="Faster backend for user registration and authentification",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:19006",
    "http://192.168.173.93:8081"
    "exp://192.168.173.93:8081",  # Expo default
    "*"  # For development - remove or restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return{
        "message": "Welcome to the User Registration API",
        "docs": "/docs",
        "version":"1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


