from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from register.main import router as register_router
from MMS.main import router as mms_router
from MMS.main import process_heartbeat_and_send_sms 
from fastapi import WebSocket

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(register_router, prefix="/api/register", tags=["Register"])
app.include_router(mms_router, prefix="/api/mms", tags=["MMS"])

# WebSocket 경로
@app.websocket("/MMS/heartbeat")
async def websocket_handler(websocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            heartbeat = data.get("heartbeat", 0)
            print(f"Received heartbeat: {heartbeat} bpm")

            # 심박수가 50 이하인지 확인하고 문자 메시지 전송
            if heartbeat <= 50:
                result = await process_heartbeat_and_send_sms(heartbeat)
                print(result)  # 문자 전송 결과 로그

            # 클라이언트에 응답
            await websocket.send_json({"status": "success", "data": {"heartbeat": heartbeat}})
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        await websocket.close()

        
@app.get("/")
def root():
    return {"message": "Unified API with WebSocket and REST"}
