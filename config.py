import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Twilio 환경 변수 가져오기
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

# 값이 정상적으로 불러와졌는지 확인 (디버깅용)
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]):
    raise ValueError("Twilio 환경 변수를 찾을 수 없습니다.")
