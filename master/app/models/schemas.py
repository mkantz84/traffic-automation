# schemas.py
# Pydantic models for request/response validation 
from pydantic import BaseModel
from typing import List
from typing import Dict

class SubmitPermutationsRequest(BaseModel):
    expected_I2: float
    expected_I3: float
    accel: List[float]
    tau: List[float]
    startupDelay: List[float] 

class ResultPayload(BaseModel):
    job_id: str
    accel: float
    tau: float
    startupDelay: float
    intersection_avg_delays: Dict[str, float]
    container_id: str 