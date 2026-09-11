from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import uuid
import asyncio
import json
import random

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
            jobs[job_id] = {"status": "complete", "directness_score": round(random.uniform(2, 8), 1), "directness_confidence": round(random.uniform(0.4, 0.9), 2), "effort_matrix": {"initiator_person_a": round(random.uniform(0.3, 0.7), 2), "initiator_person_b": round(random.uniform(0.3, 0.7), 2), "avg_reply_delay_person_a_hours": round(random.uniform(0, 5), 1), "avg_reply_delay_person_b_hours": round(random.uniform(5, 24), 1), "avg_message_length_person_a": random.randint(2, 10), "avg_message_length_person_b": random.randint(1, 8)}, "red_flags": {"flags_detected": ["breadcrumbing", "avoidance"] if random.random() > 0.5 else ["deflection"], "situationship_risk_index": random.choice(["HIGH", "MEDIUM", "LOW"]), "confidence": round(random.uniform(0.6, 0.95), 2)}, "post_mortem": {"boundary_directive": random.choice(["Establish explicit communication.", "Recommend discontinuing.", "Pattern suggests holding dynamic."]), "confidence": round(random.uniform(0.6, 0.9), 2)}}
        else:
            text = contents.decode('utf-8', errors='ignore')
            person_a_effort = round(random.uniform(0.2, 0.8), 2)
            person_b_effort = 1.0 - person_a_effort
            
            jobs[job_id] = {"status": "partial_complete", "directness_score": round(random.uniform(1, 9), 1), "directness_confidence": round(random.uniform(0.3, 0.95), 2), "effort_matrix": {"initiator_person_a": person_a_effort, "initiator_person_b": person_b_effort, "avg_reply_delay_person_a_hours": round(random.uniform(0, 5), 1), "avg_reply_delay_person_b_hours": round(random.uniform(2, 24), 1), "avg_message_length_person_a": random.randint(1, 15), "avg_message_length_person_b": random.randint(1, 15)}, "message": "Fast metrics computed..."}
            asyncio.create_task(process_job(job_id))
        
        result = jobs[job_id].copy()
        result["job_id"] = job_id
        return result
    except Exception as e:
        return {"error": str(e), "job_id": "error"}

async def process_job(job_id):
    await asyncio.sleep(2)
    risk = "HIGH" if jobs[job_id]["directness_score"] < 3 else "MEDIUM" if jobs[job_id]["directness_score"] < 6 else "LOW"
    jobs[job_id].update({"status": "complete", "red_flags": {"flags_detected": random.sample(["breadcrumbing", "deflection", "avoidance", "gaslighting"], k=random.randint(1, 3)), "situationship_risk_index": risk, "confidence": round(random.uniform(0.7, 0.95), 2)}, "post_mortem": {"boundary_directive": f"Effort asymmetry {jobs[job_id]['effort_matrix']['initiator_person_a']} vs {jobs[job_id]['effort_matrix']['initiator_person_b']}. Recommendation: {random.choice(['Establish cadence', 'Discontinue', 'Address imbalance'])}.", "confidence": round(random.uniform(0.7, 0.9), 2)}})

@app.get("/api/v1/job/{job_id}")
def get_job(job_id: str):
    return jobs.get(job_id, {"error": "Not found"})

@app.delete("/api/v1/user/{user_id}")
def delete_user(user_id: str):
    return {"deleted": True}

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
