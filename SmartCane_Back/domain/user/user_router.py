from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from database import get_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import pwd_context
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from models import User
from config import settings
from pydantic import BaseModel, EmailStr
import re
import random



# 사용자 라우터
router = APIRouter(prefix="/api/user")

# 아이디 중복 확인 라우터
@router.get("/check-id/{id}")
def check_id(id: str, db: Session = Depends(get_db)):
    # 아이디 조건 검증 (소문자 영어와 숫자만 허용)
    if not re.match("^[a-z0-9]+$", id):
        raise HTTPException(status_code=400, detail="아이디는 소문자 영어와 숫자만 포함해야 합니다.")
    
    # 중복 확인
    user = db.query(User).filter(User.id == id).first()
    if user:
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")
    
    return {"detail": "사용 가능한 아이디입니다."}

# 이메일과 인증번호 저장
email_verification_codes = {}

# 요청 데이터 모델
class EmailRequest(BaseModel):
    email: EmailStr  # 이메일 형식 검증
    
class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: int

@router.post("/send-verification-code")
def send_verification_code(request: EmailRequest, db: Session = Depends(get_db)):
    result = user_crud.send_verification_code(db, request.email)
    
    print(f"전송 상태: {result['detail']}\n")
    return result

# 인증번호 확인 라우터
@router.post("/verify-code")
def verify_code(request: VerifyCodeRequest):
    email = request.email
    code = request.code

    # 인증번호 확인
    if email not in email_verification_codes or email_verification_codes[email] != code:
        raise HTTPException(status_code=400, detail="인증번호가 올바르지 않습니다.")

    # 인증 성공 시 딕셔너리에서 삭제
    del email_verification_codes[email]
    return {"detail": "인증이 완료되었습니다."}

# 회원가입 라우터
@router.post("/signup", status_code=200)
def signup(user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    # 이메일 인증 확인
    if user_create.email not in email_verification_codes:
        raise HTTPException(status_code=400, detail="이메일 인증이 필요합니다.")

    # 이미 존재하는 사용자 확인
    user = user_crud.get_existing_user(db, user_create)
    if user:
        raise HTTPException(status_code=409, detail="이미 존재하는 사용자입니다.")
    
    # 사용자 생성
    user_crud.create_user(db, user_create)
    return {"detail": "회원가입이 성공적으로 완료되었습니다."}

# 로그인 라우터
@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 사용자명 확인 및 비밀번호 검증
    user = user_crud.get_user(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="잘못된 사용자명 또는 비밀번호", headers={"WWW-Authenticate": "Bearer"})

    # 액세스 토큰 생성
    data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

# 아이디 찾기 라우터
@router.post("/find-id")
def find_username(name: str, email: str, db: Session = Depends(get_db)):
    username = user_crud.find_username_by_name_and_email(db, name, email)
    if not username:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {"username": username}

# 비밀번호 재설정 토큰 생성
def generate_reset_token(username: str):
    # 토큰 만료 시간 설정 (예: 1시간 후)
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": username, "exp": expiration}
    reset_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return reset_token

#비밀번호 재설정 링크 검증
def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token or token expired")

#비밀번호 암호화
def hash_password(password: str):
    return pwd_context.hash(password)

# 비밀번호 찾기 라우터
@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    username = verify_reset_token(token)
    # DB에서 사용자 검색 후 비밀번호 업데이트
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password = hash_password(new_password)
    db.commit()
    return {"message": "Password reset successful"}