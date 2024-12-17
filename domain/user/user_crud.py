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
from fastapi import HTTPException
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 메모리에 인증 코드를 저장하는 딕셔너리
verification_codes = {}

def send_email(to_email: str, subject: str, content: str):
    try:
        # 이메일 메시지 생성
        message = MIMEMultipart()
        message["From"] = settings.SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = subject

        # HTML 형식의 본문 추가
        html_content = MIMEText(content, "html")
        message.attach(html_content)

        # SMTP 서버 연결 및 이메일 전송
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()  # TLS 보안 연결
            server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
            server.send_message(message)
        
        return True
    except Exception as e:
        print(f"이메일 전송 오류: {str(e)}")
        return False
    
# 인증 코드 생성 및 이메일 발송 함수
def send_verification_code(db: Session, email: str):
    try:
        # 6자리 랜덤 인증 코드 생성
        verification_code = random.randint(100000, 999999)
        verification_codes[email] = verification_code
        print(f"\n[이메일 발송 정보]")
        print(f"수신자: {email}")
        print(f"생성된 인증번호: {verification_code}")

        # 이메일 메시지 설정
        message = MIMEText(f"""
        요청하신 인증번호를 안내해드립니다.
        인증번호: {verification_code}

        감사합니다.
        """)
        message["Subject"] = "이메일 인증 코드"
        message["From"] = settings.SENDER_EMAIL
        message["To"] = email

        # SMTP 서버 연결 및 이메일 전송
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()  # TLS 보안 연결
            try:
                server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
                server.send_message(message)
                print(f"이메일 전송 성공")
                print("-" * 50)
            except Exception as login_error:
                print(f"SMTP 로그인/전송 오류: {str(login_error)}")
                raise HTTPException(status_code=500, detail="이메일 전송 실패")

        return {"detail": "인증번호가 이메일로 발송되었습니다."}
        
    except Exception as e:
        print(f"이메일 전송 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="이메일 전송 중 오류가 발생했습니다.")
    
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

    reset_token = generate_reset_token(username)
    user.reset_token = reset_token
    db.commit()

    # HTML 형식의 이메일 내용
    email_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #333;">비밀번호 재설정</h2>
                <p>비밀번호 재설정을 요청하셨습니다.</p>
                <p>아래 링크를 클릭하여 비밀번호를 재설정하세요:</p>
                <div style="margin: 20px 0;">
                    <a href="http://your-frontend-url/reset-password?token={reset_token}" 
                       style="background-color: #007bff; color: white; padding: 10px 20px; 
                              text-decoration: none; border-radius: 5px;">
                        비밀번호 재설정
                    </a>
                </div>
                <p>이 링크는 1시간 동안만 유효합니다.</p>
                <p style="color: #666; font-size: 0.9em;">본인이 요청하지 않았다면 이 이메일을 무시하세요.</p>
            </div>
        </body>
    </html>
    """

    if send_email(user.email, "비밀번호 재설정", email_content):
        return {"detail": "비밀번호 재설정 이메일이 발송되었습니다.", "token": reset_token}
    else:
        raise HTTPException(status_code=500, detail="이메일 전송 중 오류가 발생했습니다.")
