from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from register.main import router as register_router
from MMS.main import router as mms_router


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
            print(f"Received data from WebSocket: {data}")
            # 클라이언트로 응답 전송
            await websocket.send_json({"status": "success", "data": data})
    except Exception as e:
        print(f"Error in WebSocket handler: {str(e)}")
    finally:
        await websocket.close()

@app.get("/")
def root():
    return {"message": "Unified API with WebSocket and REST"}
