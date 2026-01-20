from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User, HealthData, Provider
from database import get_db
from security import get_current_user
from cryptography.fernet import Fernet
import os

router = APIRouter()

# Generate a key for encryption
def generate_key():
    return Fernet.generate_key()

# Encrypt health data
def encrypt_data(data: str, key: bytes) -> bytes:
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

# Decrypt health data
def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode()

@router.post("/share-data/{provider_id}")
async def share_health_data(provider_id: int, data: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Check if provider exists
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        # Generate encryption key and encrypt data
        key = generate_key()
        encrypted_data = encrypt_data(data, key)

        # Store encrypted data in the database
        health_data = HealthData(user_id=current_user.id, provider_id=provider_id, data=encrypted_data, key=key)
        db.add(health_data)
        db.commit()
        db.refresh(health_data)

        return {"message": "Data shared successfully", "health_data_id": health_data.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))