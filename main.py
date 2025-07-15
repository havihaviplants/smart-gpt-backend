from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sqlite3
import os

app = FastAPI()

# ✅ CORS 허용 (프론트 연동 위해 전체 허용 – 이후 도메인 제한 가능)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시에는 특정 도메인만 허용할 것
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ SQLite 초기화
DB_FILE = "leads.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        business TEXT NOT NULL,
        referral_code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# ✅ Pydantic 모델
class Lead(BaseModel):
    name: str
    phone: str
    business: str
    referral_code: Optional[str] = None

# ✅ POST /api/leads
@app.post("/api/leads")
def create_lead(lead: Lead):
    try:
        cursor.execute("""
            INSERT INTO leads (name, phone, business, referral_code)
            VALUES (?, ?, ?, ?)
        """, (lead.name, lead.phone, lead.business, lead.referral_code))
        conn.commit()
        return {"success": True, "message": "리드가 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
