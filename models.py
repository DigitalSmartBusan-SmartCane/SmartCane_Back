from sqlalchemy import Column, String, Float, Integer
from database import Base

# 사용자 테이블 모델 정의
class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True)           # 사용자 ID
    username = Column(String, unique=True, nullable=False)   # 사용자명
    password = Column(String, nullable=False)       # 해싱된 비밀번호
    email = Column(String, unique=True, nullable=False)      # 이메일
    reset_token = Column(String, nullable=True)  # 추가

#센서 데이터 테이블 모델
class SensorData(Base):
    __tablename__ = 'sensor_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ppm = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    voltage = Column(Float, nullable=False)
    time = Column(Integer, nullable=False)