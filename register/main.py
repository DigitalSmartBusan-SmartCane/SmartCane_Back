from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from register.database import insert_registration, fetch_registrations,validate_phone
import sqlite3

router = APIRouter()

class Registration(BaseModel):
    name: str
    phone: str

@router.post("/registrations")
def add_registration(registration: Registration):
    try:
        # 유효성 검사
        validate_phone(registration.phone)
        # 데이터 삽입
        insert_registration(registration.name, registration.phone)
        return {"status": "success", "message": "Registration added successfully."}
    except ValueError as e:
        if "11자리" in str(e):
            raise HTTPException(status_code=422, detail="전화번호는 정확히 11자리여야 합니다.")
        if "숫자" in str(e):
            raise HTTPException(status_code=422, detail="전화번호는 숫자만 포함해야 합니다.")
        if "Duplicate" in str(e):
            raise HTTPException(status_code=409, detail="존재하는 전화번호입니다.")
        raise HTTPException(status_code=400, detail="잘못된 요청입니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류로 인해 등록에 실패했습니다.")
  
class RelationUpdate(BaseModel):
    id: int
    relation: str  

@router.put("/registrations/relation")
def update_registration_relation(update: RelationUpdate):
    try:
        connection = sqlite3.connect("mms_data.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE mms_registration SET relation = ? WHERE id = ?", (update.relation, update.id))
        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="등록된 항목을 찾을 수 없습니다.")
        return {"status": "success", "message": "관계가 업데이트되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
    finally:
        connection.close()    
    
@router.get("/registrations")
def get_registrations():
    try:
        registrations = fetch_registrations()
        return registrations
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/registrations/{id}")
def delete_registration(id: int):
    connection = sqlite3.connect("mms_data.db")
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM mms_registration WHERE id = ?", (id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"status": "success", "message": f"Registration with id {id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()