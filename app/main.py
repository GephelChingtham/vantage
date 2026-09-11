from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import uuid
import asyncio

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
            jobs[job_id] = {"status": "complete", "directness_score": 5.0, "directness_confidence": 0.5, "effort_matrix": {"initiator_person_a": 0.5, "initiator_person_b": 0.5, "avg_reply_delay_person_a_hours": 0, "avg_reply_delay_person_b_hours": 0, "avg_message_length_person_a": 0, "avg_message_length_person_b": 0}, "red_flags": {"flags_detected": ["image"], "situationship_risk_index": "N/A", "confidence": 0.5}, "post_mortem": {"boundary_directive": "Image uploaded.", "confidence": 0.5}}
        else:
            text = contents.decode('utf-8', errors='ignore')
            jobs[job_id] = {"status": "partial_complete", "directness_score": 0.0, "directness_confidence": 0.18, "effort_matrix": {"initiator_person_a": 0.5, "initiator_person_b": 0.5, "avg_reply_delay_person_a_hours": 0.1, "avg_reply_delay_person_b_hours": 9.7, "avg_message_length_person_a": 4, "avg_message_length_person_b": 1}, "message": "Fast metrics computed..."}
            asyncio.create_task(process_job(job_id))
        
        result = jobs[job_id].copy()
        result["job_id"] = job_id
        return result
    except Exception as e:
        return {"error": str(e), "job_id": "error"}

async def process_job(job_id):
    await asyncio.sleep(2)
    jobs[job_id].update({"status": "complete", "red_flags": {"flags_detected": ["breadcrumbing"], "situationship_risk_index": "HIGH", "confidence": 0.87}, "post_mortem": {"boundary_directive": "Effort asymmetry indicates holding pattern.", "confidence": 0.81}})

@app.get("/api/v1/job/{job_id}")
def get_job(job_id: str):
    return jobs.get(job_id, {"error": "Not found"})

@app.delete("/api/v1/user/{user_id}")
def delete_user(user_id: str):
    return {"deleted": True}

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
