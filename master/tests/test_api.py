import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from app.main import app

import asyncio
from app.dal import redis_dal

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_submit_permutations_valid(monkeypatch):
    def fake_launch_worker(job_id, accel, tau, startup_delay, expected_I2, expected_I3): 
        pass
    monkeypatch.setattr("app.api.launch_worker", fake_launch_worker)
    payload = {
        "expected_I2": 50.0,
        "expected_I3": 20.0,
        "accel": [1, 2, 3],
        "tau": [1, 1.5],
        "startupDelay": [0, 0.5, 1]
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/submit_permutations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "num_simulations" in data
    assert data["num_simulations"] == 18  # 3*2*3

@pytest.mark.asyncio
async def test_submit_permutations_invalid():
    payload = {"expected_I2": 50.0}  # Missing required fields
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/submit_permutations", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.asyncio
async def test_submit_permutations_starts_workers(monkeypatch):
    calls = []
    def fake_launch_worker(job_id, accel, tau, startup_delay, expected_I2, expected_I3):
        calls.append((job_id, accel, tau, startup_delay, expected_I2, expected_I3))
    monkeypatch.setattr("app.api.launch_worker", fake_launch_worker)

    payload = {
        "expected_I2": 50.0,
        "expected_I3": 20.0,
        "accel": [1, 2, 3],
        "tau": [1, 1.5],
        "startupDelay": [0, 0.5, 1]
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/submit_permutations", json=payload)
    assert len(calls) == 18  # 3*2*3

@pytest.mark.asyncio
async def test_post_results_valid():
    payload = {
        "job_id": "test-job",
        "accel": 1.0,
        "tau": 1.5,
        "startupDelay": 0.5,
        "intersection_avg_delays": {"I2": 50.0, "I3": 20.0},
        "container_id": "dummy123"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/results", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "received"

@pytest.mark.asyncio
async def test_post_results_invalid():
    payload = {"job_id": "test-job"}  # Missing required fields
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/results", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_best_result_no_results():
    redis_dal.clear_job("test-job")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/best_result?job_id=test-job")
    assert response.status_code == 404
    assert response.json()["detail"] == "No results available for this job"

@pytest.mark.asyncio
async def test_best_result_with_results(monkeypatch):
    redis_dal.clear_job("test-job")
    redis_dal.set_expected_results("test-job", 1)
    redis_dal.add_result("test-job", {
        "accel": 1.0,
        "tau": 1.5,
        "startupDelay": 0.5,
        "intersection_avg_delays": {"I2": 50.0, "I3": 20.0},
        "error": 0.0
    })
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/best_result?job_id=test-job")
    assert response.status_code == 200
    data = response.json()
    assert data["accel"] == 1.0
    assert data["tau"] == 1.5
    assert data["startupDelay"] == 0.5
    assert "intersection_avg_delays" in data
    assert data["intersection_avg_delays"]["I2"] == 50.0
    assert data["intersection_avg_delays"]["I3"] == 20.0

@pytest.mark.asyncio
async def test_best_result_not_all_received():
    redis_dal.clear_job("test-job")
    redis_dal.set_expected_results("test-job", 3)
    redis_dal.add_result("test-job", {
        "accel": 1.0,
        "tau": 1.5,
        "startupDelay": 0.5,
        "intersection_avg_delays": {"I2": 50.0, "I3": 20.0},
        "error": 0.0
    })
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/best_result?job_id=test-job")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not all results received yet"

@pytest.mark.asyncio
async def test_job_status_not_found():
    redis_dal.clear_job("unknown-job")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/job_status?job_id=unknown-job")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

@pytest.mark.asyncio
async def test_job_status_in_progress():
    redis_dal.clear_job("job-1")
    redis_dal.set_expected_results("job-1", 3)
    redis_dal.add_result("job-1", {
        "accel": 1,
        "tau": 1,
        "startupDelay": 0,
        "intersection_avg_delays": {"I2": 10, "I3": 5},
        "error": 1.0
    })
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/job_status?job_id=job-1")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job-1"
    assert data["received_results"] == 1
    assert data["expected_results"] == 3
    assert data["complete"] is False

@pytest.mark.asyncio
async def test_job_status_complete():
    redis_dal.clear_job("job-2")
    redis_dal.set_expected_results("job-2", 2)
    redis_dal.add_result("job-2", {
        "accel": 1,
        "tau": 1,
        "startupDelay": 0,
        "intersection_avg_delays": {"I2": 10, "I3": 5},
        "error": 1.0
    })
    redis_dal.add_result("job-2", {
        "accel": 2,
        "tau": 1,
        "startupDelay": 0,
        "intersection_avg_delays": {"I2": 12, "I3": 6},
        "error": 2.0
    })
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/job_status?job_id=job-2")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job-2"
    assert data["received_results"] == 2
    assert data["expected_results"] == 2
    assert data["complete"] is True 