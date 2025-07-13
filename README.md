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
