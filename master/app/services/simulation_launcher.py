# simulation_launcher.py
# Responsible for launching worker containers

from .docker_access import DockerAccess
import logging
import os

logger = logging.getLogger(__name__)

def launch_worker(job_id, accel, tau, startup_delay, expected_I2, expected_I3):
    master_url = os.environ.get("MASTER_URL", "http://host.docker.internal:8000/api/results")
    env_vars = {
        "ACCEL": str(accel),
        "TAU": str(tau),
        "STARTUP_DELAY": str(startup_delay),
        "MASTER_URL": master_url,  # Now configurable
        "JOB_ID": job_id
    }
    container_name = f"worker_{job_id}_{accel}_{tau}_{startup_delay}".replace('.', '_')
    logger.debug(f"Launching worker with env: {env_vars} and container_name: {container_name}")
    DockerAccess.run_container(
        "simulation_worker:latest",
        env_vars,
        network_mode="host",
        container_name=container_name
    ) 