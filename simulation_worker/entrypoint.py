import os
import subprocess
import xml.etree.ElementTree as ET
import requests
import json

# Read parameters from environment variables
ACCEL = float(os.environ["ACCEL"])
TAU = float(os.environ["TAU"])
STARTUP_DELAY = float(os.environ["STARTUP_DELAY"])
MASTER_URL = os.environ["MASTER_URL"]  # e.g., http://master:8000/results

VTYPES_XML = "hw_model.vtypes.xml"

# Update vtypes.xml with the given parameters
def update_vtypes_xml(accel, tau, startup_delay, xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for vtype in root.findall(".//vType"):
        vtype.set("accel", str(accel))
        vtype.set("tau", str(tau))
        vtype.set("startupDelay", str(startup_delay))
    tree.write(xml_path)

update_vtypes_xml(ACCEL, TAU, STARTUP_DELAY, VTYPES_XML)

# Run the simulation script and capture output
result = subprocess.run(["python", "run_simulation.py"], capture_output=True, text=True)

# Parse the output JSON (assuming run_simulation.py prints JSON result)
try:
    output = result.stdout.strip()
    sim_result = json.loads(output)
except Exception as e:
    print(f"Failed to parse simulation output: {e}\nOutput was: {result.stdout}")
    exit(1)

# Add parameters to the result if not present
sim_result["accel"] = ACCEL
sim_result["tau"] = TAU
sim_result["startupDelay"] = STARTUP_DELAY

# Post the result to the master
try:
    resp = requests.post(MASTER_URL, json=sim_result)
    print(f"Posted result to master: {resp.status_code} {resp.text}")
except Exception as e:
    print(f"Failed to post result to master: {e}")
    exit(1) 