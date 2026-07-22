import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
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
    title="Dental Records Patient Onboarding",
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


CANONICAL_HOST = os.getenv("CANONICAL_HOST", "dental-records.com").strip().lower()
REDIRECT_HOSTS = {
    host.strip().lower()
    for host in os.getenv(
        "REDIRECT_HOSTS",
        "www.dental-records.com,app.dental-records.com",
    ).split(",")
    if host.strip()
}


@app.middleware("http")
async def redirect_to_canonical_host(request: Request, call_next):
    host = request.headers.get("host", "").split(":")[0].lower()
    if CANONICAL_HOST and host in REDIRECT_HOSTS and host != CANONICAL_HOST:
        redirect_url = request.url.replace(scheme="https", netloc=CANONICAL_HOST)
        return RedirectResponse(url=str(redirect_url), status_code=301)

    return await call_next(request)


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

@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/login")
def login_page():
    return FileResponse("frontend/login.html")


@app.get("/register")
def register_page():
    return FileResponse("frontend/register.html")


@app.get("/dashboard")
def dashboard_page():
    return FileResponse("frontend/dashboard.html")


@app.get("/profile")
def profile_page():
    return FileResponse("frontend/profile.html")


@app.get("/appointments")
def appointments_page():
    return FileResponse("frontend/appointments.html")


@app.get("/radiographs")
def radiographs_page():
    return FileResponse("frontend/radiographs.html")


@app.get("/{page_name}.html")
def legacy_html_page(page_name: str):
    clean_routes = {
        "index": "/",
        "login": "/login",
        "register": "/register",
        "dashboard": "/dashboard",
        "profile": "/profile",
        "appointments": "/appointments",
        "radiographs": "/radiographs",
    }
    if page_name not in clean_routes:
        return FileResponse(f"frontend/{page_name}.html")
    return RedirectResponse(url=clean_routes[page_name], status_code=301)


# Include routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(appointments.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend_root")
