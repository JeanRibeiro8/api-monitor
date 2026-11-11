from app.services import monitor_service


def test_check_404_is_a_response_not_connection_error(client, monkeypatch):
    class FakeResponse:
        status_code = 404
        def iter_bytes(self):
            yield b"not found"
        def __enter__(self): return self
        def __exit__(self, *args): return False

    class FakeClient:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def stream(self, *args, **kwargs): return FakeResponse()

    monkeypatch.setattr(monitor_service.httpx, "Client", FakeClient)
    monkeypatch.setattr(monitor_service, "validate_public_target", lambda url: None)

    created = client.post("/monitors", json={"name": "Example", "url": "https://example.com"})
    result = client.post(f"/monitors/{created.json()['id']}/check")
    assert result.status_code == 200
    assert result.json()["status_code"] == 404
    assert result.json()["is_available"] is False
    assert result.json()["error_message"] is None


def test_dashboard_summary(client):
    client.post("/monitors", json={"name": "Example", "url": "https://example.com"})
    response = client.get("/dashboard/summary")
    assert response.status_code == 200
    assert response.json()["total_monitors"] == 1
