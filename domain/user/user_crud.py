from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate
from models import User
from domain.user.user_schema import UserFindRequest
import secrets
import smtplib
from email.mime.text import MIMEText
import random
from jose import jwt
from datetime import datetime, timedelta
from config import settings


# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 메모리에 인증 코드를 저장하는 딕셔너리
verification_codes = {}
# 인증 코드 생성 및 이메일 발송 함수
def send_verification_code(db: Session, email: str):
    # 4자리 랜덤 인증 코드 생성
    verification_code = random.randint(1000, 9999)
    verification_codes[email] = verification_code  # 메모리에 인증 코드 저장

    # 이메일 전송 내용 작성
    message = MIMEText(f"인증 코드: {verification_code}")
    message["Subject"] = "이메일 인증 코드"
    message["From"] = settings.SENDER_EMAIL
    message["To"] = email

    try:
        # SMTP 서버 연결 및 이메일 전송
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
            server.sendmail(settings.SENDER_EMAIL, email, message.as_string())
        return {"detail": "인증번호가 이메일로 발송되었습니다."}
    except Exception as e:
        raise Exception(f"이메일 전송 중 오류가 발생했습니다: {str(e)}")

# 인증 코드 확인 함수
def verify_code(email: str, code: int):
    stored_code = verification_codes.get(email)
    if not stored_code:
        raise Exception("인증 코드가 존재하지 않습니다.")
    if stored_code != code:
        raise Exception("인증 코드가 일치하지 않습니다.")
    # 인증 성공 시 인증 코드 삭제
    del verification_codes[email]
    return {"detail": "이메일 인증이 완료되었습니다."}

# 새 사용자 생성 함수
def create_user(db: Session, user_create: UserCreate):
    db_user = User(
        id=user_create.id,
        username=user_create.username,
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

