# traffic-automation

Model Calibration Using Simulation

## Project Structure

This is a monorepo containing:

- `master/` - FastAPI backend + React frontend (master service)
- `simulation_worker/` - SUMO simulation worker container

## Getting Started

### Prerequisites

- Python 3.11+
- Docker
- Node.js (for frontend)

### Master Service Setup

1. Navigate to the master directory:

```bash
cd master
```

2. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the master service:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

---

## Docker & Docker Compose

This project is fully containerized. You can build and run the entire stack (backend, frontend, Redis, and simulation worker image) using Docker Compose.

### Build and Run

From the project root:

```bash
docker compose --profile build-only build
```

Then start the stack:

```bash
docker compose up
```

- The backend (FastAPI + React) will be available at [http://localhost:8000](http://localhost:8000)
- Redis will be available on port 6379
- The simulation worker image will be built and is launched dynamically by the backend as jobs are submitted

### Notes

- The backend container requires access to the Docker socket to launch worker containers. This is handled by mounting `/var/run/docker.sock` into the backend container via Docker Compose.
- The `simulation-worker` service in `docker-compose.yml` is only for building the image; actual workers are launched by the backend.
- You can monitor logs with:
  ```bash
  docker compose logs -f
  ```
- To stop and remove all containers:
  ```bash
  docker compose down
  ```

---

### API Endpoints

- `GET /` - Health check
- `POST /submit_permutations` - Submit parameter permutations for simulation
- `POST /results` - Receive simulation results from workers
- `GET /best_result` - Get the best result found so far

### Running Tests

```bash
cd master
source venv/bin/activate
pytest
```
