from os import getenv
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from sqlalchemy.orm import Session

from app.models.database import get_db, SessionLocal
from app.utils.auth import bootstrap_key_user, get_user_from_cookie
from app.utils.network import check_wifi_connected, setup_ap_mode, is_raspberry_pi_zero
from app.routers import device, admin, auth

# Create FastAPI app with enhanced documentation
app = FastAPI(
    title="Raspberry Pi Device Manager",
    description="API for managing Raspberry Pi Zero devices with AP/LAN mode and role-based access control",
    version="1.0.0",
    docs_url="/api/docs",  # Custom Swagger UI URL
    redoc_url="/api/redoc",  # Custom ReDoc URL
    openapi_url="/api/openapi.json",  # Custom OpenAPI schema URL
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication operations"
        },
        {
            "name": "device",
            "description": "Device-facing endpoints for hit tracking and channel assignment"
        },
        {
            "name": "admin",
            "description": "Admin-facing endpoints for device and user management"
        }
    ]
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(device.router)
app.include_router(admin.router)
app.include_router(auth.router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect root to login page"""
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    """Render dashboard page with authentication check"""
    # Check if user is authenticated using cookie
    user = get_user_from_cookie(request, db)
    
    if not user:
        # Redirect to login page if not authenticated
        return RedirectResponse(url="/login", status_code=303)
    
    # User is authenticated, render dashboard with user info
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request, 
            "username": user.username,
            "is_key_user": user.is_key_user
        }
    )

def startup_tasks():
    """Perform startup tasks before running the app"""
    # Get database session
    db = SessionLocal()
    
    try:
        # Bootstrap key user if needed
        bootstrap_key_user(db)
        
        # Only run AP mode setup on Raspberry Pi Zero
        if is_raspberry_pi_zero():
            # Check network connection
            if not check_wifi_connected():
                # Setup AP mode if not connected to Wi-Fi
                ap_password = setup_ap_mode()
                print(f"AP mode activated with password: {ap_password}")
        else:
            print("Not running on a Raspberry Pi Zero - skipping AP mode setup")
    finally:
        db.close()

if __name__ == "__main__":
    # Run startup tasks
    startup_tasks()
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=getenv("ENV") == "development"
    )
