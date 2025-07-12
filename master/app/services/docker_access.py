import docker
import logging

logger = logging.getLogger(__name__)

class DockerAccess:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = docker.from_env()
        return cls._client

    @classmethod
    def run_container(cls, image, env_vars, network_mode="host", container_name=None):
        client = cls.get_client()
        if container_name:
            env_vars = dict(env_vars)
            env_vars["CONTAINER_ID"] = container_name
        logger.info(f"Running container: {image} with env: {env_vars} and name: {container_name}")
        return client.containers.run(
            image,
            detach=True,
            environment=env_vars,
            network_mode=network_mode,
            name=container_name
        )

    @classmethod
    def remove_container(cls, container_id):
        client = cls.get_client()
        try:
            container = client.containers.get(container_id)
            container.remove(force=True)
            logger.info(f"Removed container {container_id}")
        except Exception as e:
            logger.warning(f"Could not remove container {container_id}: {e}") 