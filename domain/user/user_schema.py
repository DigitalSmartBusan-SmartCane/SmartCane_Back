import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

# 회원가입 데이터 검증 모델
class UserCreate(BaseModel):
    id: str
    username: str = Field(..., min_length=1, max_length=50, description="사용자명")
    password1: str
    password2: str
    email: EmailStr

    # 필수 항목 비어있지 않도록 검증
    @field_validator('id', 'username', 'password1', 'password2', 'email')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('필수 항목을 입력해주세요')
        return v
    
    # id는 영어 소문자와 숫자만 포함하도록 정규식 검증
    @field_validator('id')
    def validate_id(cls, v):
        if not re.match("^[a-z0-9]+$", v):
            raise ValueError('id는 소문자 영어와 숫자만 포함할 수 있습니다.')
        return v
    
    @field_validator('phone')
    def check_phone(cls, v):
        # 전화번호 형식이 01012345678처럼 11자리 숫자인지 확인하는 정규식
        if not re.match(r"^010\d{8}$", v):
            raise ValueError('올바른 형식의 번호를 입력해주세요')
        return v
    
    # password1은 8자리 이상 영문, 숫자, 특수문자 포함해야 함
    @field_validator('password1')
    def validate_password1(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 8자리 이상이어야 합니다.')
        
        # 영문자, 숫자, 특수문자 각각 포함 여부 체크
        if not any(char.isdigit() for char in v):
            raise ValueError('비밀번호에는 숫자가 포함되어야 합니다.')
        if not any(char.isalpha() for char in v):
            raise ValueError('비밀번호에는 영문자가 포함되어야 합니다.')
        if not any(char in '!@#$%^&*()_+[]{}|;:,.<>?/~' for char in v):
            raise ValueError('비밀번호에는 특수문자가 포함되어야 합니다.')

        return v
    
    # password1과 password2가 일치하는지 검증
    @field_validator("password2")
    def passwords_match(cls, v, info):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return v

# 토큰 응답 모델
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


# 아이디 찾기 요청 모델
class UserFindRequest(BaseModel):
    name: str
    email: EmailStr

# 비밀번호 재설정 요청 모델
class UserPasswordResetRequest(BaseModel):
    username: str
    email: EmailStr





