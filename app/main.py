from fastapi import FastAPI
from app.api import router as api_router
from config import load_config

app = FastAPI()

@app.on_event("startup")
def startup_event():
    # Load and validate configuration once at startup
    load_config("config")

app.include_router(api_router)
