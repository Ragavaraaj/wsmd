from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models.database import get_db
from app.utils.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["auth"])

@router.post("/token")
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Generate a JWT token for authenticated users and set it as a cookie
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "is_key_user": user.is_key_user}, 
        expires_delta=access_token_expires
    )
    
    # Set the token as a cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access to the cookie
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
        path="/"       # Make cookie available for all paths
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_key_user": user.is_key_user
    }

@router.post("/logout")
def logout(response: Response):
    """
    Clear the authentication cookie to log out the user
    """
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}
