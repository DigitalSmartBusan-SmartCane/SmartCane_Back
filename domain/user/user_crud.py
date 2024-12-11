from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate
from models import User
from domain.user.user_schema import UserFindRequest
import secrets
import smtplib
from email.mime.text import MIMEText

from jose import jwt
from datetime import datetime, timedelta
from config import settings

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 새 사용자 생성 함수
def create_user(db: Session, user_create: UserCreate):
    db_user = User(id=user_create.id, username=user_create.username,
                password=pwd_context.hash(user_create.password1),
                email=user_create.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # 새로 추가된 사용자 정보를 가져옴

    return db_user  # 생성된 사용자 반환

# 기존 사용자 조회 함수
def get_existing_user(db: Session, user_create: UserCreate):
    return db.query(User).filter(
        (User.username == user_create.username) |
        (User.email == user_create.email)
    ).first()

# 사용자명으로 사용자 조회 함수 (로그인용)
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# 아이디 찾기 함수 (이름과 이메일로 사용자 찾기)
def find_username_by_name_and_email(db: Session, name: str, email: str):
    # 이름과 이메일로 사용자를 검색
    user = db.query(User).filter(User.username == name, User.email == email).first()
    if user:
        return user.id  # 아이디 반환
    return None 

# generate_reset_token 함수 추가
def generate_reset_token(username: str):
    # 토큰 만료 시간 설정 (1시간)
    expiration = datetime.utcnow() + timedelta(hours=1)
    data = {
        "sub": username,
        "exp": expiration
    }
    reset_token = jwt.encode(
        data, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return reset_token

# 비밀번호 재설정 요청 함수
def request_password_reset(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    # 인증 토큰 생성
    reset_token = generate_reset_token(username)

    # 사용자 정보에 reset_token 저장
    user.reset_token = reset_token  # 사용자 모델에 reset_token을 추가해야 합니다.
    db.commit()

    # 이메일 전송
    message = MIMEText(f"비밀번호를 재설정하려면 다음 링크를 클릭하세요:{reset_token}")
    message["Subject"] = "비밀번호 재설정 요청"
    message["From"] = settings.SENDER_EMAIL
    message["To"] = user.email

    # SMTP 서버 연결 및 이메일 전송
    with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER_EMAIL, user.email, message.as_string())

    return reset_token

