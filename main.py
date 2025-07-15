from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Supabase 설정이 누락되었습니다.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실서비스 시엔 도메인 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 리드 입력 모델
class Lead(BaseModel):
    name: str
    phone: str
    business: str
    referral_code: Optional[str] = None

# ✅ POST /api/leads → Supabase 저장
@app.post("/api/leads")
def create_lead(lead: Lead):
    try:
        response = supabase.table("leads").insert({
            "name": lead.name,
            "phone": lead.phone,
            "business": lead.business,
            "referral_code": lead.referral_code,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return {"success": True, "message": "리드가 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ GET /api/leads → Supabase 조회
@app.get("/api/leads")
def get_leads():
    try:
        response = supabase.table("leads").select("*").order("created_at", desc=True).execute()
        return {"leads": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
