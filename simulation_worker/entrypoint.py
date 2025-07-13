import os
import subprocess
import requests
import json
import logging
from xml_utils import update_vtypes_xml
import time
from retry_utils import retry_with_backoff
import sys

# Ensure SUMO_HOME and PYTHONPATH are set for SUMO tools
os.environ["SUMO_HOME"] = os.environ.get("SUMO_HOME", "/usr/share/sumo")
os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + ":/usr/share/sumo/tools"

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

# Parse simulation result from result.json file
try:
    with open("result.json") as f:
        sim_result = json.load(f)
    logger.info(f"Parsed simulation result: {sim_result}")
except Exception as e:
    logger.error(f"Failed to read or parse result.json: {e}")
    logger.error("Exiting with status code 1 due to simulation output parsing failure.")
    exit(1)

# Add parameters to the result if not present
sim_result["accel"] = ACCEL
sim_result["tau"] = TAU
sim_result["startupDelay"] = STARTUP_DELAY
if JOB_ID:
    sim_result["job_id"] = JOB_ID
if CONTAINER_ID:
    sim_result["container_id"] = CONTAINER_ID

# Post the result to the master with retry (only for 5** error codes), exponential backoff, and circuit breaker
def post_result():
    logger.info(f"Posting result to master at {MASTER_URL} ...")
    resp = requests.post(MASTER_URL, json=sim_result, timeout=10)
    logger.info(f"Posted result to master: {resp.status_code} {resp.text}")
    if 400 <= resp.status_code < 500:
        logger.error(f"Client error {resp.status_code}: {resp.text}. Exiting container.")
        sys.exit(1)
    if 500 <= resp.status_code < 600:
        raise RuntimeError(f"Server error {resp.status_code}: {resp.text}")
    return resp

try:
    retry_with_backoff(post_result, retry_exceptions=(RuntimeError,))
except Exception:
    logger.error("Failed to post result to master after retries. Exiting with status code 1.")
    exit(1) 