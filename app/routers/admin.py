from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import asyncio
import json
from typing import List
from pydantic import BaseModel, Field

from app.models.database import User, Device, get_db
from app.utils.auth import get_key_user, get_password_hash, get_current_user_from_cookie, get_key_user_from_cookie

# Pydantic models for request/response validation and documentation
class DeviceModel(BaseModel):
    mac_address: str = Field(..., description="MAC address of the device")
    order: int = Field(..., description="Order assigned to the device")
    hit_counter: int = Field(..., description="Current hit counter value")
    max_hits: int = Field(100, description="Maximum allowed hits for the device")
    name: str = Field(None, description="Optional name for the device")
    
    class Config:
        from_attributes = True

class UserModel(BaseModel):
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    is_key_user: bool = Field(..., description="Whether the user has key user privileges")
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str = Field(..., description="Response message")

# Create router with more detailed description
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized - Authentication required"},
        403: {"description": "Forbidden - Key user required for certain operations"}
    },
)

@router.post("/device", response_model=MessageResponse, summary="Update Device Properties")
def update_device(
    request: Request,
    mac_address: str = Form(...),
    order: int = Form(...),
    max_hits: int = Form(...),
    name: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Update multiple properties for a specific device.
    
    Parameters:
    - **mac_address**: MAC address of the device to update
    - **order**: New order value to assign
    - **max_hits**: New maximum hit count value
    - **name**: New name for the device (optional)
    
    Returns a success message.
    
    Raises:
    - 404 Not Found: If the device with the given MAC address doesn't exist
    
    Note:
    - If name is not provided, a name will be auto-generated based on MAC address and order
    """
    device = db.query(Device).filter(Device.mac_address == mac_address).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Update device properties
    device.order = order
    device.max_hits = max_hits
    
    if name:
        device.name = name
    elif not device.name:
        # Auto-generate name if none provided and none exists
        device.name = f"Device-{mac_address[-6:].replace(':', '')}-O{order}"
    
    db.commit()
    
    return {"message": "Device properties updated successfully"}

@router.post("/user", response_model=MessageResponse, summary="Create New User")
def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    is_key_user: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_key_user_from_cookie)  # Only key users can create users
):
    """
    Create a new user account.
    
    Parameters:
    - **username**: Unique username for the new account
    - **password**: Password for the new account
    - **is_key_user**: Whether the new user should have key user privileges (defaults to false)
    
    Returns a success message.
    
    Raises:
    - 400 Bad Request: If the username already exists or there's an error creating the user
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        password_hash=hashed_password,
        is_key_user=is_key_user
    )
    
    try:
        db.add(new_user)
        db.commit()
        return {"message": "User created successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating user")

@router.post("/user/password", response_model=MessageResponse, summary="Update User Password")
def update_user_password(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_key_user_from_cookie)  # Only key users can update passwords
):
    """
    Update an existing user's password.
    
    Parameters:
    - **username**: Username of the account to update
    - **password**: New password for the account
    
    Returns a success message.
    
    Raises:
    - 404 Not Found: If the user with the given username doesn't exist
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password_hash = get_password_hash(password)
    db.commit()
    
    return {"message": "Password updated successfully"}

# Helper function to get formatted device data
def get_device_data(db: Session):
    devices = db.query(Device).all()
    return [{
        "mac_address": device.mac_address,
        "order": device.order,
        "hit_counter": device.hit_counter,
        "max_hits": device.max_hits,
        "name": device.name
    } for device in devices]

# Helper function to get formatted user data
def get_user_data(db: Session, is_key_user: bool):
    if not is_key_user:
        return None
    users = db.query(User).all()
    return [{"id": user.id, "username": user.username, "is_key_user": user.is_key_user} for user in users]

# Helper function to create SSE event message
def create_event(event_name, data):
    return f"event: {event_name}\ndata: {json.dumps(data)}\n\n"

# Generate SSE events
async def generate_sse_events(request: Request, db: Session, current_user: User):
    # Send connection established event
    yield "event: connected\ndata: Connection established\n\n"
    
    # Get initial data
    is_key_user = current_user.is_key_user
    
    # Initial data payload
    users_data = get_user_data(db, is_key_user)
    if users_data:
        yield create_event("users", users_data)
    
    devices_data = get_device_data(db)
    yield create_event("devices", devices_data)
    
    # Track last known state to avoid sending duplicate data
    last_devices_hash = hash(str(devices_data))
    last_users_hash = hash(str(users_data)) if users_data else None
    heartbeat_counter = 0
    
    try:
        # Continue sending updates
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                print(f"Client disconnected: {request.client.host}")
                break
            
            # Check for device updates
            new_devices_data = get_device_data(db)
            current_devices_hash = hash(str(new_devices_data))
            if current_devices_hash != last_devices_hash:
                yield create_event("devices", new_devices_data)
                last_devices_hash = current_devices_hash
            
            # Check for user updates if key user
            if is_key_user:
                new_users_data = get_user_data(db, True)
                current_users_hash = hash(str(new_users_data))
                if current_users_hash != last_users_hash:
                    yield create_event("users", new_users_data)
                    last_users_hash = current_users_hash
            
            # Send heartbeat periodically
            heartbeat_counter += 1
            if heartbeat_counter >= 5:  # Every 5 iterations (3s * 5 = 15s)
                yield create_event("heartbeat", {"timestamp": asyncio.get_event_loop().time()})
                heartbeat_counter = 0
            
            # Wait before checking for updates again
            await asyncio.sleep(3)
            
    except Exception as e:
        # Log the error and notify the client
        print(f"SSE error: {str(e)}")
        yield create_event("error", {"message": str(e)})

@router.get("/events", summary="Server-Sent Events Stream")
async def sse_events(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Establishes a Server-Sent Events (SSE) connection for real-time updates.
    
    The endpoint streams device and user data updates in real-time without requiring polling.
    
    Returns:
    - A streaming response containing JSON-formatted events for device and user data
    """
    return StreamingResponse(
        generate_sse_events(request, db, current_user), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering for Nginx
        }
    )

@router.get("/devices", response_model=List[DeviceModel], summary="Get All Devices")
def get_all_devices(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Retrieve a list of all devices in the system.
    
    Returns a list of all registered devices with their current status information.
    """
    devices = db.query(Device).all()
    return devices

@router.get("/users", response_model=List[UserModel], summary="Get All Users")
def get_all_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_key_user_from_cookie)
):
    """
    Retrieve a list of all users in the system.
    
    Returns information about all users including their ID, username, and privilege level.
    
    This endpoint requires key user privileges.
    """
    users = db.query(User).all()
    return users
