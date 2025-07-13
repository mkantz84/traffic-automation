import redis
import json
import os

def result_param_key(job_id, accel, tau, startup_delay):
    return f"job:{job_id}:result:{accel}:{tau}:{startup_delay}"

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

# Results (O(1) overwrite by param key)

def set_result(job_id, accel, tau, startup_delay, result_dict):
    r = RedisClient.get_instance()
    key = result_param_key(job_id, accel, tau, startup_delay)
    r.set(key, json.dumps(result_dict))


def get_results(job_id):
    r = RedisClient.get_instance()
    pattern = f"job:{job_id}:result:*"
    keys = r.keys(pattern)
    keys_checked = ensure_type(keys, list, "result_keys")
    results = []
    for key in keys_checked:
        data = r.get(key)
        if data:
            data_checked = ensure_type(data, (str, bytes), "result_data")
            if isinstance(data_checked, bytes):
                data_checked = data_checked.decode()
            results.append(json.loads(data_checked))
    return results

def get_results_count(job_id):
    r = RedisClient.get_instance()
    pattern = f"job:{job_id}:result:*"
    keys = r.keys(pattern)
    keys_checked = ensure_type(keys, list, "result_keys")
    return len(keys_checked)

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