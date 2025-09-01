from datetime import datetime, timedelta, timezone
from typing import Optional
import getpass
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models.database import User, get_db

# Security configurations
SECRET_KEY = "CHANGE_THIS_TO_A_SECURE_SECRET_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate a password hash"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current user from the JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_key_user(current_user: User = Depends(get_current_user)):
    """Check if the current user is a key user"""
    if not current_user.is_key_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Key user required."
        )
    return current_user

def get_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Get the current user from JWT token in a cookie"""
    token = request.cookies.get("access_token")
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Get the current user from JWT token in a cookie and verify authentication"""
    user = get_user_from_cookie(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_key_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Check if the current user from cookie is a key user"""
    user = get_user_from_cookie(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_key_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Key user required."
        )
    return user

def bootstrap_key_user(db: Session):
    """Bootstrap a key user if none exists"""
    # Check if any user exists
    if db.query(User).first() is not None:
        return False
    
    print("\n=================================")
    print("FIRST RUN - CREATE KEY USER")
    print("=================================")
    
    # Prompt for username and password
    username = input("Enter key username: ")
    password = getpass.getpass("Enter key password: ")
    confirm_password = getpass.getpass("Confirm key password: ")
    
    if password != confirm_password:
        print("Passwords do not match. Please try again.")
        return bootstrap_key_user(db)
    
    # Create the key user
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        password_hash=hashed_password,
        is_key_user=True
    )
    
    db.add(new_user)
    db.commit()
    
    print("\nKey user created successfully!")
    return True
