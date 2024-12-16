import sqlite3

DB_PATH = "mms_data.db"

def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
  CREATE TABLE IF NOT EXISTS mms_registration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    relation TEXT DEFAULT ''
);

    """)
    connection.commit()
    connection.close()

def insert_registration(name, phone): 
    if not is_phone_unique(phone):  # 중복 여부 확인
        raise ValueError(f"Duplicate phone number: {phone}")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO mms_registration (name, phone) VALUES (?, ?)", (name, phone))
        connection.commit()
    except sqlite3.IntegrityError:
        raise ValueError("이미 존재하는 전화번호입니다.")
    except Exception as e:
        raise e
   
    finally:
        connection.close()


def fetch_registrations():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, phone, relation FROM mms_registration")
    rows = cursor.fetchall()
    connection.close()
    return [{"id": row[0], "name": row[1], "phone": str(row[2]), "relation": row[3]} for row in rows]


def update_relation(id, relation):
    """
    관계 정보를 업데이트
    """
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("UPDATE mms_registration SET relation = ? WHERE id = ?", (relation, id))
    connection.commit()
    connection.close()
    
# 전화번호 중복 확인
def is_phone_unique(phone):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT 1 FROM mms_registration WHERE phone = ?", (phone,))
    result = cursor.fetchone()
    connection.close()
    return result is None  # 중복되지 않은 경우 True 반환

# 전화번호 형식 검증
def validate_phone(phone: str):
    if not phone.isdigit():
        raise ValueError("전화번호는 숫자만 포함해야 합니다.")
    if len(phone) != 11 :
        raise ValueError("전화번호는 11자리여야 합니다.")


def reset_table():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS mms_registration")  # 기존 테이블 삭제
    connection.commit()
    connection.close()

# 초기화 함수 실행
init_db()
