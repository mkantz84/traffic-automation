import os
import subprocess
import requests
import json
import logging
from xml_utils import update_vtypes_xml
import time
from retry_utils import retry_with_backoff

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Read parameters from environment variables
ACCEL = float(os.environ["ACCEL"])
TAU = float(os.environ["TAU"])
STARTUP_DELAY = float(os.environ["STARTUP_DELAY"])
MASTER_URL = os.environ["MASTER_URL"]  # e.g., http://master:8000/results
JOB_ID = os.environ.get("JOB_ID")
CONTAINER_ID = os.environ.get("CONTAINER_ID")

logger.info(f"Starting simulation worker with parameters: accel={ACCEL}, tau={TAU}, startupDelay={STARTUP_DELAY}, job_id={JOB_ID}, container_id={CONTAINER_ID}")
logger.info(f"Master URL: {MASTER_URL}")

VTYPES_XML = "hw_model.vtypes.xml"

# Use the xml_utils module to update vtypes.xml
update_vtypes_xml(ACCEL, TAU, STARTUP_DELAY, VTYPES_XML)

# Run the simulation script and capture output
logger.info("Running simulation...")
result = subprocess.run(["python", "run_simulation.py"], capture_output=True, text=True)
logger.info("Simulation output:")
logger.info(result.stdout)
if result.stderr:
    logger.error("Simulation error output:")
    logger.error(result.stderr)

# Parse only the last line of output as JSON
try:
    output_lines = result.stdout.strip().splitlines()
    json_line = output_lines[-1]  # Get the last line
    sim_result = json.loads(json_line)
    logger.info(f"Parsed simulation result: {sim_result}")
except Exception as e:
    logger.error(f"Failed to parse simulation output: {e}\nOutput was: {result.stdout}")
    exit(1)

# Add parameters to the result if not present
sim_result["accel"] = ACCEL
sim_result["tau"] = TAU
sim_result["startupDelay"] = STARTUP_DELAY
if JOB_ID:
    sim_result["job_id"] = JOB_ID
if CONTAINER_ID:
    sim_result["container_id"] = CONTAINER_ID

# Post the result to the master with retry, exponential backoff, and circuit breaker

def post_result():
    logger.info(f"Posting result to master at {MASTER_URL} ...")
    resp = requests.post(MASTER_URL, json=sim_result, timeout=10)
    logger.info(f"Posted result to master: {resp.status_code} {resp.text}")
    return resp

try:
    retry_with_backoff(post_result)
except Exception:
    exit(1) 