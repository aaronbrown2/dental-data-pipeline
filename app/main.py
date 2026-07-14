from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .database import SessionLocal, engine
from . import models
from .routers import auth, patients, appointments
from .seed_demo import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield

# Initialize FastAPI app
app = FastAPI(
    title="Dental AI Patient Onboarding",
    description="A patient management system for dental practices",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_csp_header(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://kit.fontawesome.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "font-src 'self' https://kit.fontawesome.com; "
        "img-src 'self' data:; "
        "connect-src 'self' https: https://cdn.jsdelivr.net; "
        "frame-ancestors 'none'; "
    )
    return response



# Mount static files for serving uploaded radiographs
#app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
