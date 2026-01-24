from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User, HealthData, Provider
from database import get_db
from security import get_current_user
from pydantic import BaseModel
import json
import os
import requests

router = APIRouter()

class ShareHealthDataRequest(BaseModel):
    provider_id: int
    data: dict

@router.post("/share_health_data")
async def share_health_data(request: ShareHealthDataRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        provider = db.query(Provider).filter(Provider.id == request.provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        health_data = HealthData(user_id=current_user.id, provider_id=request.provider_id, data=json.dumps(request.data))
        db.add(health_data)
        db.commit()
        db.refresh(health_data)

        # Securely send data to the provider's endpoint
        response = requests.post(provider.endpoint, json=request.data, headers={"Authorization": f"Bearer {os.getenv('PROVIDER_API_KEY')}"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to share data with provider")

        return {"message": "Health data shared successfully", "health_data_id": health_data.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))