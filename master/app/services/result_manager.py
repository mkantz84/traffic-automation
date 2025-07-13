# result_manager.py
# Responsible for collecting and analyzing results 

from app.dal import redis_dal
from .docker_access import DockerAccess
from app.utils import calculate_error
import logging

logger = logging.getLogger(__name__)

def set_expected_delays(job_id, expected_I2, expected_I3):
    redis_dal.set_expected_delays(job_id, expected_I2, expected_I3)

def set_expected_results(job_id, count):
    redis_dal.set_expected_results(job_id, count)

def calculate_result_error(payload, result):
    expected = redis_dal.get_expected_delays(payload.job_id)
    assert isinstance(expected, dict), "Expected delays must be a dict"
    if expected and "I2" in expected and "I3" in expected:
        expected_I2 = float(expected["I2"])
        expected_I3 = float(expected["I3"])
        return calculate_error(result["intersection_avg_delays"], {"I2": expected_I2, "I3": expected_I3})
    return None

def update_best_result(job_id, result):
    best = redis_dal.get_best_result(job_id)
    if best is None or (result["error"] is not None and (best.get("error") is None or result["error"] < best["error"])):
        redis_dal.set_best_result(job_id, result)
        logger.info(f"Updated best_result for job {job_id}")

def remove_worker_container(container_id):
    DockerAccess.remove_container(container_id)

def store_result(payload):
    result = {
        "accel": payload.accel,
        "tau": payload.tau,
        "startupDelay": payload.startupDelay,
        "intersection_avg_delays": payload.intersection_avg_delays
    }
    result["error"] = calculate_result_error(payload, result)
    redis_dal.set_result(payload.job_id, payload.accel, payload.tau, payload.startupDelay, result)
    logger.info(f"Stored result in Redis for job {payload.job_id}")
    update_best_result(payload.job_id, result)
    remove_worker_container(payload.container_id)

def get_best_result(job_id):
    best_result = redis_dal.get_best_result(job_id)
    if not best_result:
        return None
    return best_result

def all_results_received(job_id):
    expected = redis_dal.get_expected_results(job_id)
    if expected is None:
        return False
    received = redis_dal.get_results_count(job_id)
    return received >= expected

def has_any_results(job_id):
    return redis_dal.get_results_count(job_id) > 0

def get_job_status(job_id):
    expected = redis_dal.get_expected_results(job_id)
    if expected is None:
        return None
    received = redis_dal.get_results_count(job_id)
    return {
        "job_id": job_id,
        "received_results": received,
        "expected_results": expected,
        "complete": received == expected
    }