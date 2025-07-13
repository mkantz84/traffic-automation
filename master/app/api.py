import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import SubmitPermutationsRequest, ResultPayload
from app.services.simulation_launcher import launch_worker
from app.services import result_manager
import itertools
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/submit_permutations")
def submit_permutations(request: SubmitPermutationsRequest):
    logger.info(f"Received /submit_permutations with job parameters: {request}")
    permutations = list(itertools.product(request.accel, request.tau, request.startupDelay))
    job_id = str(uuid.uuid4())
    # Store expected delays and count for this job
    result_manager.set_expected_delays(job_id, request.expected_I2, request.expected_I3)
    result_manager.set_expected_results(job_id, len(permutations))
    for accel, tau, startup_delay in permutations:
        launch_worker(job_id, accel, tau, startup_delay, request.expected_I2, request.expected_I3)
    return {
        "job_id": job_id,
        "num_simulations": len(permutations)
    }

@router.post("/results")
def post_results(payload: ResultPayload):
    result_manager.store_result(payload)
    return {"status": "received"}

@router.get("/best_result")
def get_best_result(job_id: str):
    # Check if there are any results at all
    if not result_manager.has_any_results(job_id):
        raise HTTPException(status_code=404, detail="No results available for this job")
    
    # Check if all results have been received
    if not result_manager.all_results_received(job_id):
        raise HTTPException(status_code=404, detail="Not all results received yet")
    
    best_result = result_manager.get_best_result(job_id)
    if best_result is None:
        raise HTTPException(status_code=404, detail="No results available for this job")
    return best_result 

@router.get("/job_status")
def job_status(job_id: str):
    status = result_manager.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status 