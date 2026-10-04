from fastapi.testclient import TestClient
from plat.main import app
client = TestClient(app)

def test_pass_fail():
    assert client.post("/check", json={'env': 'dev', 'template': 'python-service', 'owner': 'ada', 'image': 'api:1.2.3'}).json()["passed"] is True
    bad = client.post("/check", json={'env': 'prod', 'template': 'python-service', 'owner': 'ada', 'image': 'api:1.2.3'}).json()
    assert bad["passed"] is False
    assert "env" in bad["failed"]
