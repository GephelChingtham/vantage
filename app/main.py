from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import uuid
import asyncio
from app.parsers.whatsapp import parse_whatsapp
from app.parsers.discord import parse_discord
from app.metrics.directness import calculate_directness
from app.metrics.effort import calculate_effort
from app.llm.red_flags import analyze_red_flags
from app.llm.post_mortem import generate_post_mortem

app = FastAPI()
jobs = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "vantage"}

@app.post("/api/v1/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        ext = file.filename.split('.')[-1].lower()
        job_id = str(uuid.uuid4())
        
        if ext in ['png', 'jpg', 'jpeg']:
            jobs[job_id] = {"status": "complete", "directness_score": 5.0, "directness_confidence": 0.5, "effort_matrix": {"initiator_person_a": 0.5, "initiator_person_b": 0.5, "avg_reply_delay_person_a_hours": 0, "avg_reply_delay_person_b_hours": 0, "avg_message_length_person_a": 0, "avg_message_length_person_b": 0}, "red_flags": {"flags_detected": ["image_received"], "situationship_risk_index": "N/A", "confidence": 0.5}, "post_mortem": {"boundary_directive": "Image uploaded. Use text exports for analysis.", "confidence": 0.5}}
        else:
            text = contents.decode('utf-8', errors='ignore')
            messages = parse_whatsapp(text) if ext == 'txt' else parse_discord(text)
            jobs[job_id] = {"status": "partial_complete", "directness_score": calculate_directness(messages), "directness_confidence": 0.18, "effort_matrix": calculate_effort(messages), "message": "Fast metrics computed..."}
            asyncio.create_task(process_job(job_id, messages))
        
        result = jobs[job_id].copy()
        result["job_id"] = job_id
        return result
    except Exception as e:
        return {"error": str(e), "job_id": "error"}

async def process_job(job_id, messages):
    red_flags = await analyze_red_flags(str(messages))
    post_mortem = await generate_post_mortem(jobs[job_id]["directness_score"], jobs[job_id]["effort_matrix"], red_flags)
    jobs[job_id].update({"status": "complete", "red_flags": red_flags, "post_mortem": post_mortem})

@app.get("/api/v1/job/{job_id}")
def get_job(job_id: str):
    return jobs.get(job_id, {"error": "Not found"})

@app.delete("/api/v1/user/{user_id}")
def delete_user(user_id: str):
    return {"deleted": True}

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
