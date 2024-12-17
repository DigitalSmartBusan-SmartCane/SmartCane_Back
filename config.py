import secrets

class Settings:
# 환경 설정값들
    SECRET_KEY = secrets.token_hex(32)  # 비밀 키
    ALGORITHM = "HS256"  # 알고리즘
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 토큰 만료 시간 (1일)
    
    # Gmail SMTP 설정
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587  # TLS 포트
    SENDER_EMAIL = "dlxogns.lg39@gmail.com"  # 발신자 Gmail 주소
    SENDER_PASSWORD = ""   # Gmail 앱 비밀번호 16자리
    


settings = Settings()