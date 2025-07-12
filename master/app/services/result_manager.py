# result_manager.py
# Responsible for collecting and analyzing results 

from .docker_access import DockerAccess
from app.utils import calculate_error
import logging

logger = logging.getLogger(__name__)

_results = {}
_expected_delays = {}

def set_expected_delays(job_id, expected_I2, expected_I3):
    _expected_delays[job_id] = {"I2": expected_I2, "I3": expected_I3}

def store_result(payload):
    result = {
        "accel": payload.accel,
        "tau": payload.tau,
        "startupDelay": payload.startupDelay,
        "intersection_avg_delays": payload.intersection_avg_delays
    }
    if payload.job_id not in _results:
        _results[payload.job_id] = []
        
    # Compute error using expected delays
    expected = _expected_delays.get(payload.job_id)
    if expected:
        result["error"] = calculate_error(result["intersection_avg_delays"], expected)
    else:
        result["error"] = None
    _results[payload.job_id].append(result)
    logger.info(f"_results={_results}")

    # Remove the container after storing the result
    container_id = payload.container_id
    DockerAccess.remove_container(container_id)