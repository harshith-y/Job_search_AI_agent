from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

API_TOKEN = os.getenv("API_TOKEN")

@app.get("/seen_jobs")
def get_seen_jobs(authorization: str = Header(None)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        with open("seen_job.txt", "r", encoding="utf-8") as f:
            jobs = [line.strip() for line in f if line.strip()]
        return JSONResponse(content={"seen_jobs": jobs})
    except FileNotFoundError:
        return JSONResponse(content={"seen_jobs": []})

