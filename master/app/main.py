from fastapi import FastAPI
from .api import router
from .logging_config import setup_logging

setup_logging()

app = FastAPI()

app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "ok"} 