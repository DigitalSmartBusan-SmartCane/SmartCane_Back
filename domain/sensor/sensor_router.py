from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import SensorData
from pydantic import BaseModel

# 센서 라우터
router =  APIRouter(prefix="/api/sensor")

# 수신할 데이터 모델 정의
class SensorDataSchema(BaseModel):
    ppm: float
    temperature: float
    humidity: float
    voltage: float
    time: int

# 여러 센서 데이터를 한번에 수신하는 엔드포인트
@router.post("/upload-sensor-data")
def upload_sensor_data(data: List[SensorDataSchema], db: Session = Depends(get_db)):
    for entry in data:
        sensor_data = SensorData(
            ppm=entry.ppm,
            temperature=entry.temperature,
            humidity=entry.humidity,
            voltage=entry.voltage,
            time=entry.time
        )
        db.add(sensor_data)
    db.commit()
    return {"status": "success", "message": "Data uploaded successfully"}
