import uvicorn
from fastapi import FastAPI
from database import engine
import models
from domain.user import user_router
from domain.sensor import sensor_router

# 데이터베이스 테이블을 생성
models.Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 사용자 라우터 등록
app.include_router(user_router.router)

# 센서 데이터 라우터 등록
app.include_router(sensor_router.router)

# 메인 함수로 실행할 때 애플리케이션을 실행
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True)
