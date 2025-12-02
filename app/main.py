from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import auth, patients, appointments

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Dental AI Patient Onboarding",
    description="A patient management system for dental practices",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving uploaded radiographs
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Include routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(appointments.router)

@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/frontend/")

@app.get("/health")
def health_check():
    return {"status": "healthy"}