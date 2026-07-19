import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock, AsyncMock, patch

client = TestClient(app)

def test_run_simulation_success():
    class MockSimulationResponse:
        parsed = {
            "risk_matrix_score": 8,
            "multilingual_pa_drafts": {"en": "Evacuate Zone A", "es": "Evacuar Zona A"},
            "crowd_reroute_logic": ["Open Gate 4", "Redirect from Gate 3"]
        }
        
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=MockSimulationResponse())
    
    with patch("google.genai.Client", return_value=mock_client):
        payload = {"scenario": "Fire detected near Gate 3"}
        response = client.post("/api/v1/simulate/", json=payload)
        
        assert response.status_code == 200
        assert response.json()["risk_matrix_score"] == 8
        assert "en" in response.json()["multilingual_pa_drafts"]

def test_alru_cache_intercepts_duplicate_simulation():
    from app.api.simulator import _cached_simulate
    import asyncio
    _cached_simulate.cache_clear()
    
    class MockSimulationResponse:
        parsed = {
            "risk_matrix_score": 4,
            "multilingual_pa_drafts": {"en": "Monitor"},
            "crowd_reroute_logic": ["None"]
        }
        
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=MockSimulationResponse())
    
    with patch("google.genai.Client", return_value=mock_client):
        async def run_cache():
            await _cached_simulate("Minor leak", "{}")
            hits_before = _cached_simulate.cache_info().hits
            await _cached_simulate("Minor leak", "{}")
            hits_after = _cached_simulate.cache_info().hits
            return hits_before, hits_after
            
        hits_before, hits_after = asyncio.run(run_cache())
        assert hits_after > hits_before
