from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.models.database import Device, get_db
from app.utils.network import get_client_mac, next_available_order

# Create Pydantic models for request/response validation and documentation
class OrderResponse(BaseModel):
    order: int = Field(..., description="The assigned order number")
    assigned: int = Field(..., description="The assigned order number (duplicate for backward compatibility)")

class HitCounterResponse(BaseModel):
    counter: int = Field(..., description="The current hit counter value")
    max_hits: int = Field(..., description="The maximum allowed hits for the device")
    order: int = Field(..., description="The current order assigned to the device")

# Create router with more detailed description
router = APIRouter(
    prefix="/device",
    tags=["device"],
    responses={404: {"description": "Not found"}},
)

@router.post("/hit", response_model=HitCounterResponse, summary="Increment Hit Counter")
def increment_hit_counter(request: Request, db: Session = Depends(get_db)):
    """
    Increment the hit counter for a device identified by its MAC address.
    
    The MAC address is automatically detected from the client's connection.
    
    Returns:
    - The updated hit counter value
    - The maximum hits allowed for the device
    - The current order assigned to the device
    
    Raises:
    - 400 Bad Request: If the device MAC address cannot be determined or the device is not found
    
    Note: When hit_counter reaches max_hits, it will be automatically reset to 0 by the database trigger.
    A device name is automatically generated if not already present.
    """
    # Get client MAC address
    mac_address = get_client_mac(request)
    if not mac_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not determine device MAC address"
        )
    
    # Find device in database or create new entry
    device = db.query(Device).filter(Device.mac_address == mac_address).first()
    
    if not device:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device not found"
        )
    else:
        # If device doesn't have a name, generate one
        if not device.name:
            device.name = f"Device-{mac_address[-6:].replace(':', '')}-O{device.order}"
        
        device.hit_counter += 1
    
    db.commit()
    
    # After commit, we need to refresh the device to get the actual hit_counter value
    # in case the trigger reset it to 0
    db.refresh(device)
    
    # Return response
    return {
        "counter": device.hit_counter,
        "max_hits": device.max_hits,
        "order": device.order
    }

@router.post("/register", response_model=OrderResponse, summary="Request Order Assignment")
def register_device(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a device and assign an order number.
    
    The MAC address is automatically detected from the client's connection.
    
    - The next available order number will be assigned
    - If the device already exists, it will return the existing order
    - A device name is automatically generated if not already present
    
    Returns:
    - The assigned order number
    
    Raises:
    - 400 Bad Request: If the device MAC address cannot be determined
    """
    # Get client MAC address
    mac_address = get_client_mac(request)
    if not mac_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not determine device MAC address"
        )

    
    # Find device in database or create new entry
    device = db.query(Device).filter(Device.mac_address == mac_address).first()
    
    if not device:
        assigned_order = next_available_order(db)
        # Generate a default name based on MAC address and order
        default_name = f"Device-{mac_address[-6:].replace(':', '')}-O{assigned_order}"
            
        device = Device(
            mac_address=mac_address,
            hit_counter=0,
            order=assigned_order,
            name=default_name
        )
        db.add(device)
    else:
        # If device doesn't have a name, generate one
        if not device.name:
            device.name = f"Device-{mac_address[-6:].replace(':', '')}-O{device.order}"
    
    # Save changes
    db.commit()
    
    # Return response
    return {
        "order": device.order,
        "assigned": device.order
    }
