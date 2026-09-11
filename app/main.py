import os
import uuid
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.db.models import AnalysisJobDB, UserDB
from app.parsers.whatsapp import WhatsAppParser
from app.parsers.discord import DiscordParser
from app.metrics.directness import DirectnessAnalyzer
from app.metrics.effort import EffortAnalyzer
from app.llm.red_flags import analyze_red_flags
from app.llm.post_mortem import generate_post_mortem

app = FastAPI(
    title="Vantage",
    description="Communication auditor for analyzing effort asymmetry and intent",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "vantage"}

@app.post("/api/v1/analyze")
async def analyze(file: UploadFile = File(...), db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    user_id = "user_demo"
    
    try:
        content = await file.read()
        text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File read error: {str(e)}")
    
    if file.filename.endswith(".txt"):
        parser = WhatsAppParser()
        source_format = "whatsapp"
    elif file.filename.endswith(".json"):
        parser = DiscordParser()
        source_format = "discord"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format (use .txt or .json)")
    
    try:
        messages = parser.parse(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {str(e)}")
    
    if not messages:
        raise HTTPException(status_code=400, detail="No messages found in file")
    
    job = AnalysisJobDB(
        job_id=job_id,
        user_id=user_id,
        status="processing",
        source_format=source_format,
        message_count=len(messages),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(job)
    db.commit()
    
    directness_analyzer = DirectnessAnalyzer(messages)
    directness = directness_analyzer.analyze()
    
    effort_analyzer = EffortAnalyzer(messages)
    effort = effort_analyzer.analyze()
    
    job.directness_score = directness.score
    job.effort_matrix = effort.dict()
    job.status = "partial_complete"
    db.commit()
    
    async def run_llm_analysis():
        try:
            messages_text = "\n".join([f"{m.sender}: {m.text}" for m in messages[:50]])
            
            red_flags = await analyze_red_flags(messages_text)
            post_mortem = await generate_post_mortem(
                directness.score,
                effort.dict(),
                red_flags
            )
            
            job.red_flags = red_flags
            job.post_mortem = post_mortem
            job.status = "complete"
            db.commit()
        except Exception as e:
            job.status = "failed"
            db.commit()
    
    asyncio.create_task(run_llm_analysis())
    
    return {
        "job_id": job_id,
        "status": "partial_complete",
        "directness_score": directness.score,
        "directness_confidence": directness.confidence,
        "effort_matrix": effort.dict(),
        "message": "Fast metrics computed. Heavy analysis running async..."
    }

@app.get("/api/v1/job/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AnalysisJobDB).filter_by(job_id=job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.job_id,
        "status": job.status,
        "directness_score": job.directness_score,
        "effort_matrix": job.effort_matrix,
        "red_flags": job.red_flags,
        "post_mortem": job.post_mortem
    }

@app.delete("/api/v1/user/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    db.query(AnalysisJobDB).filter_by(user_id=user_id).update({"is_deleted": True})
    db.query(UserDB).filter_by(user_id=user_id).delete()
    db.commit()
    
    return {"status": "deleted", "user_id": user_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
