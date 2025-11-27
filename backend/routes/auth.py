from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from db import get_db
from models import ChefDB, ChefRegister, ChefLogin, ChefResponse, Token
from auth import get_password_hash, verify_password, create_access_token, verify_token, get_current_user
from datetime import timedelta
import os
import json
import urllib.request
import random
import string

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=ChefResponse)
async def register_chef(chef: ChefRegister, db: Session = Depends(get_db)):
    # Check if email already exists
    db_chef = db.query(ChefDB).filter(ChefDB.email == chef.email).first()
    if db_chef:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if username already exists
    db_chef = db.query(ChefDB).filter(ChefDB.username == chef.username).first()
    if db_chef:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new chef
    hashed_password = get_password_hash(chef.password)
    db_chef = ChefDB(
        email=chef.email,
        username=chef.username,
        full_name=chef.full_name,
        hashed_password=hashed_password,
        restaurant_name=chef.restaurant_name,
        restaurant_location=chef.restaurant_location,
        cuisine_specialty=chef.cuisine_specialty,
        experience_years=chef.experience_years,
        phone=chef.phone
    )
    
    db.add(db_chef)
    db.commit()
    db.refresh(db_chef)
    
    return db_chef

@router.post("/google", response_model=Token)
async def google_sign_in(payload: dict, db: Session = Depends(get_db)):
    id_token = payload.get("id_token")
    email = payload.get("email")
    name = payload.get("name")
    
    if not id_token and not email:
        raise HTTPException(status_code=400, detail="Missing authentication data")

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        # Allow manual OAuth flow without client ID verification for development
        if email and not id_token:
            # Manual OAuth flow - trust the provided email (it was verified on frontend)
            name = name or "Chef"
            
            if not email:
                raise HTTPException(status_code=400, detail="Email not available from Google")
            
            db_chef = db.query(ChefDB).filter(ChefDB.email == email).first()
            if not db_chef:
                base_username = (email.split("@")[0]).replace(" ", "").lower()
                username = base_username
                suffix = 1
                while db.query(ChefDB).filter(ChefDB.username == username).first():
                    username = f"{base_username}{suffix}"
                    suffix += 1

                random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                db_chef = ChefDB(
                    email=email,
                    username=username,
                    full_name=name,
                    hashed_password=get_password_hash(random_password),
                    is_verified=True,
                )
                db.add(db_chef)
                db.commit()
                db.refresh(db_chef)
            else:
                from datetime import datetime
                db_chef.last_login = datetime.utcnow()
                db.commit()

            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": db_chef.email}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=500, detail="Google client ID not configured")

    # Handle both ID token verification and manual OAuth flow
    if id_token:
        # Verify Google ID token
        try:
            with urllib.request.urlopen(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}") as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid Google token")

        if data.get("aud") != client_id:
            raise HTTPException(status_code=401, detail="Invalid token audience")

        email = data.get("email")
        name = data.get("name") or "Chef"
    elif email:
        # Manual OAuth flow - trust the provided email (it was verified on frontend)
        name = name or "Chef"
    else:
        raise HTTPException(status_code=400, detail="Email not available from Google")

    if not email:
        raise HTTPException(status_code=400, detail="Email not available from Google")

    db_chef = db.query(ChefDB).filter(ChefDB.email == email).first()
    if not db_chef:
        base_username = (email.split("@")[0]).replace(" ", "").lower()
        username = base_username
        suffix = 1
        while db.query(ChefDB).filter(ChefDB.username == username).first():
            username = f"{base_username}{suffix}"
            suffix += 1

        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        db_chef = ChefDB(
            email=email,
            username=username,
            full_name=name,
            hashed_password=get_password_hash(random_password),
            is_verified=True,
        )
        db.add(db_chef)
        db.commit()
        db.refresh(db_chef)
    else:
        from datetime import datetime
        db_chef.last_login = datetime.utcnow()
        db.commit()

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_chef.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_chef(chef: ChefLogin, db: Session = Depends(get_db)):
    # Find chef by email
    db_chef = db.query(ChefDB).filter(ChefDB.email == chef.email).first()
    if not db_chef:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    # Check if chef is active
    if not db_chef.is_active:
        raise HTTPException(
            status_code=401,
            detail="Account is deactivated"
        )
    
    # Verify password
    if not verify_password(chef.password, db_chef.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    # Update last login
    from datetime import datetime
    db_chef.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_chef.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=ChefResponse)
async def get_current_chef(current_user_email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    db_chef = db.query(ChefDB).filter(ChefDB.email == current_user_email).first()
    if not db_chef:
        raise HTTPException(
            status_code=404,
            detail="Chef not found"
        )
    return db_chef

@router.put("/me", response_model=ChefResponse)
async def update_chef_profile(
    chef_update: ChefRegister, 
    current_user_email: str = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_chef = db.query(ChefDB).filter(ChefDB.email == current_user_email).first()
    if not db_chef:
        raise HTTPException(
            status_code=404,
            detail="Chef not found"
        )
    
    # Update fields
    db_chef.full_name = chef_update.full_name
    db_chef.restaurant_name = chef_update.restaurant_name
    db_chef.restaurant_location = chef_update.restaurant_location
    db_chef.cuisine_specialty = chef_update.cuisine_specialty
    db_chef.experience_years = chef_update.experience_years
    db_chef.phone = chef_update.phone
    
    # Update password if provided
    if chef_update.password:
        db_chef.hashed_password = get_password_hash(chef_update.password)
    
    db.commit()
    db.refresh(db_chef)
    
    return db_chef