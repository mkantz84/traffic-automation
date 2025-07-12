import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app

import asyncio

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_submit_permutations_valid():
    payload = {
        "expected_I2": 50.0,
        "expected_I3": 20.0,
        "accel": [1, 2, 3],
        "tau": [1, 1.5],
        "startupDelay": [0, 0.5, 1]
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/submit_permutations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "num_simulations" in data
    assert data["num_simulations"] == 18  # 3*2*3

@pytest.mark.asyncio
async def test_submit_permutations_invalid():
    payload = {"expected_I2": 50.0}  # Missing required fields
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/submit_permutations", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.asyncio
async def test_post_results_valid():
    payload = {
        "job_id": "test-job",
        "accel": 1.0,
        "tau": 1.5,
        "startupDelay": 0.5,
        "intersection_avg_delays": {"I2": 50.0, "I3": 20.0}
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/results", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "received"

@pytest.mark.asyncio
async def test_post_results_invalid():
    payload = {"job_id": "test-job"}  # Missing required fields
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/results", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_best_result_no_results():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/best_result")
    assert response.status_code == 404
    assert response.json()["detail"] == "No results available"

@pytest.mark.asyncio
async def test_best_result_with_results(monkeypatch):
    # Simulate a result in the result manager
    from app.services import result_manager
    result_manager._results = {
        "test-job": {
            "accel": 1.0,
            "tau": 1.5,
            "startupDelay": 0.5,
            "intersection_avg_delays": {"I2": 50.0, "I3": 20.0},
            "error": 0.0
        }
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/best_result")
    assert response.status_code == 200
    data = response.json()
    assert data["accel"] == 1.0
    assert data["tau"] == 1.5
    assert data["startupDelay"] == 0.5
    assert "intersection_avg_delays" in data
    assert data["intersection_avg_delays"]["I2"] == 50.0
    assert data["intersection_avg_delays"]["I3"] == 20.0 