from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
import os

app = FastAPI(title="Food Calorie App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Router registrations will be added in subsequent tasks
# from routers import upload, meals, recognize, foods, stats
