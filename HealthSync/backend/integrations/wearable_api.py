import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

class WearableDataRequest(BaseModel):
    device: str
    user_id: str

class WearableDataResponse(BaseModel):
    heart_rate: int
    steps: int
    sleep_hours: float

@router.post("/fetch_wearable_data", response_model=WearableDataResponse)
async def fetch_wearable_data(request: WearableDataRequest):
    try:
        if request.device == "fitbit":
            return await fetch_fitbit_data(request.user_id)
        elif request.device == "garmin":
            return await fetch_garmin_data(request.user_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported device")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_fitbit_data(user_id: str) -> WearableDataResponse:
    url = f"https://api.fitbit.com/1/user/{user_id}/activities/date/today.json"
    headers = {
        "Authorization": f"Bearer {os.getenv('FITBIT_ACCESS_TOKEN')}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from Fitbit")
    
    data = response.json()
    heart_rate = data['activities-heart'][0]['value']['restingHeartRate']
    steps = data['summary']['steps']
    sleep_hours = data['sleep'][0]['duration'] / 3600000 if data['sleep'] else 0

    return WearableDataResponse(heart_rate=heart_rate, steps=steps, sleep_hours=sleep_hours)

async def fetch_garmin_data(user_id: str) -> WearableDataResponse:
    url = f"https://api.garmin.com/wellness-api/rest/user/{user_id}/activities"
    headers = {
        "Authorization": f"Bearer {os.getenv('GARMIN_ACCESS_TOKEN')}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from Garmin")
    
    data = response.json()
    heart_rate = data['heartRate']
    steps = data['steps']
    sleep_hours = data['sleepDuration'] / 3600 if 'sleepDuration' in data else 0

    return WearableDataResponse(heart_rate=heart_rate, steps=steps, sleep_hours=sleep_hours)