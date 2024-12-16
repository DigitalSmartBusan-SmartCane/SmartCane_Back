import secrets

class Settings:
# 환경 설정값들
    SECRET_KEY = secrets.token_hex(32)  # 비밀 키
    ALGORITHM = "HS256"  # 알고리즘
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 토큰 만료 시간 (1일)

    SMTP_SERVER = "smtp.gmail.com"  # 예시
    SMTP_PORT = 465
    SENDER_EMAIL = "your-email@example.com"
    SENDER_PASSWORD = "your-app-password"

settings = Settings()