import redis
import json
import os

class RedisClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )
        return cls._instance

def ensure_type(value, expected_type, context):
    if not isinstance(value, expected_type):
        raise RuntimeError(f"Redis client returned a non-{expected_type.__name__} value for {context}. You are likely using an async Redis client. Please use the synchronous redis-py package.")
    return value

# Expected results

def set_expected_results(job_id, count):
    r = RedisClient.get_instance()
    r.set(f"job:{job_id}:expected_results", count)

def get_expected_results(job_id):
    r = RedisClient.get_instance()
    val = r.get(f"job:{job_id}:expected_results")
    if val is None:
        return None
    val_checked = ensure_type(val, (str, bytes), "expected_results")
    if isinstance(val_checked, bytes):
        val_checked = val_checked.decode()
    return int(val_checked)

# Expected delays

def set_expected_delays(job_id, expected_I2, expected_I3):
    r = RedisClient.get_instance()
    r.hset(f"job:{job_id}:expected_delays", mapping={"I2": expected_I2, "I3": expected_I3})

def get_expected_delays(job_id):
    r = RedisClient.get_instance()
    delays = r.hgetall(f"job:{job_id}:expected_delays")
    return ensure_type(delays, dict, "expected_delays")

# Results (list of JSON strings)

def add_result(job_id, result_dict):
    r = RedisClient.get_instance()
    r.rpush(f"job:{job_id}:results", json.dumps(result_dict))

def get_results(job_id):
    r = RedisClient.get_instance()
    results = r.lrange(f"job:{job_id}:results", 0, -1)
    results_checked = ensure_type(results, list, "results")
    return [json.loads(x) for x in results_checked]

def get_results_count(job_id):
    r = RedisClient.get_instance()
    count = r.llen(f"job:{job_id}:results")
    return ensure_type(count, int, "results_count")

# For tests: clear all job data

def clear_job(job_id):
    r = RedisClient.get_instance()
    r.delete(f"job:{job_id}:expected_results")
    r.delete(f"job:{job_id}:expected_delays")
    r.delete(f"job:{job_id}:results")

def set_best_result(job_id, result_dict):
    r = RedisClient.get_instance()
    r.set(f"job:{job_id}:best_result", json.dumps(result_dict))

def get_best_result(job_id):
    r = RedisClient.get_instance()
    val = r.get(f"job:{job_id}:best_result")
    if val is None:
        return None
    val_checked = ensure_type(val, (str, bytes), "best_result")
    if isinstance(val_checked, bytes):
        val_checked = val_checked.decode()
    return json.loads(val_checked) 