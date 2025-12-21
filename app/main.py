from fastapi import FastAPI, Response
from app.api import router as api_router
from config import load_config
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

@app.on_event("startup")
def startup_event():
    load_config("config")


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


app.include_router(api_router)
