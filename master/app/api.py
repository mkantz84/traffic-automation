import logging
from fastapi import APIRouter
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
    # Store expected delays for this job
    result_manager.set_expected_delays(job_id, request.expected_I2, request.expected_I3)
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