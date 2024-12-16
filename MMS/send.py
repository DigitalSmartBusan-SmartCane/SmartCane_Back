from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(to_number: str, heart_rate: int):
    """
    Twilio를 사용하여 SMS 발송 (심박수 포함 메시지 생성)
    """
    # +82 국가 코드 추가 (필요 시)
    if not to_number.startswith("+82"):
        to_number = "+82"+to_number.lstrip("0")  # 0으로 시작하는 번호 제거

    message_body = f"심박수 이상치 탐지! 현재 심박수: {heart_rate} bpm"
    print(f"전송 대상 번호: {to_number}, 메시지 내용: {message_body}")
    try:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_FROM_NUMBER,
            to=to_number
        )
        print(f"문자 메시지 전송 성공")
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        print(f"문자 메시지 전송 실패: {e}")
        return {"status": "error", "message": str(e)}