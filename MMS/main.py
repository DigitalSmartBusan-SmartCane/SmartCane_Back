import sys
import os
# 현재 디렉토리보다 상단에 있는 BACKEND 부터 경로지정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from MMS.send import send_sms
from register.database import fetch_registrations

router = APIRouter()

# 심박수 데이터 모델
class HeartbeatData(BaseModel):
    heartbeat: int
    
@router.post("/heartbeat")
async def process_heartbeat(data: HeartbeatData):
    try:
        # 심박수 데이터 처리 및 SMS 발송
        result = await process_heartbeat_and_send_sms(data.heartbeat)
        return result
    except Exception as e:
        print(f"심박수 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 오류")
    
# 핸들러 함수
async def process_heartbeat_and_send_sms(heartbeat: int):
    """
    심박수를 처리하고 기준치 이하일 경우 문자 메시지 발송
    """
    print(f"현재 심박수: {heartbeat}")
    
    if heartbeat < 60:
        registrations = fetch_registrations()
        print(f"Fetched registrations: {registrations}")

        if not registrations:
            print("등록된 전화번호가 없습니다.")
            return {"status": "error", "message": "등록된 전화번호가 없습니다."}

        # 등록된 전화번호로 SMS 발송
        for registration in registrations:
            try:
                response = send_sms(to_number=registration["phone"], heart_rate=heartbeat)
                if response["status"] != "success":
                    print(f"SMS 전송 실패: {response['message']}")
            except Exception as e:
                print(f"SMS 전송 중 오류: {str(e)}")
        
        return {"status": "success", "message": "심박수 이상 탐지 및 메시지 발송 완료."}

