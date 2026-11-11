def test_create_and_list_monitor(client):
    response = client.post("/monitors", json={
        "name": "Example", "url": "https://example.com", "check_interval": 60
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Example"
    listing = client.get("/monitors")
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_update_and_delete_monitor(client):
    created = client.post("/monitors", json={"name": "Before", "url": "https://example.com"})
    monitor_id = created.json()["id"]
    updated = client.patch(f"/monitors/{monitor_id}", json={"name": "After"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "After"
    deleted = client.delete(f"/monitors/{monitor_id}")
    assert deleted.status_code == 204
    assert client.get(f"/monitors/{monitor_id}").status_code == 404


def test_reject_non_http_url(client):
    response = client.post("/monitors", json={"name": "Bad", "url": "ftp://example.com"})
    assert response.status_code == 422
