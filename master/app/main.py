from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router
from .logging_config import setup_logging

setup_logging()

app = FastAPI()

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok"} 