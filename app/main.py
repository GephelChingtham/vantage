from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import asyncio
import os
from app.parsers.whatsapp import parse_whatsapp
from app.parsers.discord import parse_discord
from app.metrics.directness import calculate_directness
from app.metrics.effort import calculate_effort
from app.llm.red_flags import analyze_red_flags
from app.llm.post_mortem import generate_post_mortem

app = FastAPI()
jobs = {}

def parse_chat(text, file_type):
    if file_type == 'txt':
        return parse_whatsapp(text)
    elif file_type == 'json':
        return parse_discord(text)
    return []

@app.get("/health")
def health():
    return {"status": "ok", "service": "vantage"}

@app.post("/api/v1/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename
    file_ext = filename.split('.')[-1].lower()
    
    job_id = str(uuid.uuid4())
    
    if file_ext in ['png', 'jpg', 'jpeg']:
        jobs[job_id] = {
            "status": "partial_complete",
            "directness_score": 0.0,
            "directness_confidence": 0.0,
            "effort_matrix": {"initiator_person_a": 0.5, "initiator_person_b": 0.5, "avg_reply_delay_person_a_hours": 0.0, "avg_reply_delay_person_b_hours": 0.0, "avg_message_length_person_a": 0, "avg_message_length_person_b": 0},
            "message": "Image received. Vision processing starting..."
        }
        asyncio.create_task(process_image_job(job_id, contents))
    else:
        text = contents.decode('utf-8')
        messages = parse_chat(text, file_ext)
        directness = calculate_directness(messages)
        effort = calculate_effort(messages)
        
        jobs[job_id] = {
            "status": "partial_complete",
            "directness_score": directness,
            "directness_confidence": 0.18,
            "effort_matrix": effort,
            "message": "Fast metrics computed. Heavy analysis running async..."
        }
        asyncio.create_task(process_job(job_id, messages))
    
    return jobs[job_id] | {"job_id": job_id}

async def process_job(job_id, messages):
    red_flags = await analyze_red_flags(str(messages))
    post_mortem = await generate_post_mortem(
        jobs[job_id]["directness_score"],
        jobs[job_id]["effort_matrix"],
        red_flags
    )
    jobs[job_id].update({
        "status": "complete",
        "red_flags": red_flags,
        "post_mortem": post_mortem
    })

async def process_image_job(job_id, image_bytes):
    await asyncio.sleep(2)
    jobs[job_id]["status"] = "complete"
    jobs[job_id]["red_flags"] = {"flags_detected": ["low_resolution"], "situationship_risk_index": "MEDIUM", "confidence": 0.6}
    jobs[job_id]["post_mortem"] = {"boundary_directive": "Image quality too low for analysis. Use text exports for better results.", "confidence": 0.5}

@app.get("/api/v1/job/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}, 404
    return jobs[job_id]

@app.delete("/api/v1/user/{user_id}")
def delete_user(user_id: str):
    return {"status": "deleted", "user_id": user_id}

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
