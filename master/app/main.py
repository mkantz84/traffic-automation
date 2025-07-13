from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import router
from .logging_config import setup_logging

setup_logging()

app = FastAPI()

app.include_router(router, prefix="/api")

# Serve built frontend static files
app.mount("/", StaticFiles(directory="frontend-dist", html=True), name="frontend")

@app.get("/healthz")
def health_check():
    return {"status": "ok"} 