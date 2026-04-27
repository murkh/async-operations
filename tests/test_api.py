from bson import ObjectId
import pytest

from app.services.redis_service import redis_service


@pytest.fixture
def valid_user_id():
    return str(ObjectId())


@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["mongodb"] == "ok"
    assert response.json()["redis"] == "ok"


@pytest.mark.asyncio
async def test_create_document(async_client, valid_user_id):
    payload = {
        "user_id": valid_user_id,
        "title": "Test Doc",
        "content": "This is a test document.",
    }
    response = await async_client.post("/api/v1/documents", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "queued"
    assert data["title"] == "Test Doc"

    # Check queue length in redis
    queue_len = await redis_service.redis_client.llen(redis_service.queue_name)
    assert queue_len == 1


@pytest.mark.asyncio
async def test_get_document(async_client, valid_user_id):
    # Create one first
    payload = {
        "user_id": valid_user_id,
        "title": "Get Doc",
        "content": "Get this content",
    }
    create_resp = await async_client.post("/api/v1/documents", json=payload)
    doc_id = create_resp.json()["id"]

    # Get it
    response = await async_client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["id"] == doc_id
    assert response.json()["title"] == "Get Doc"


@pytest.mark.asyncio
async def test_list_documents(async_client, valid_user_id):
    # Create two
    for i in range(2):
        payload = {
            "user_id": valid_user_id,
            "title": f"Doc {i}",
            "content": f"Content {i}",
        }
        await async_client.post("/api/v1/documents", json=payload)

    # List them
    response = await async_client.get(f"/api/v1/documents?user_id={valid_user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_update_document(async_client, valid_user_id):
    # Create one
    payload = {
        "user_id": valid_user_id,
        "title": "Old Title",
        "content": "Old Content",
    }
    create_resp = await async_client.post("/api/v1/documents", json=payload)
    doc_id = create_resp.json()["id"]

    # Update it
    update_payload = {"title": "New Title"}
    response = await async_client.patch(f"/api/v1/documents/{doc_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"
    assert response.json()["content"] == "Old Content"


@pytest.mark.asyncio
async def test_delete_document(async_client, valid_user_id):
    # Create one
    payload = {
        "user_id": valid_user_id,
        "title": "To Delete",
        "content": "Delete me",
    }
    create_resp = await async_client.post("/api/v1/documents", json=payload)
    doc_id = create_resp.json()["id"]

    # Delete it
    response = await async_client.delete(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await async_client.get(f"/api/v1/documents/{doc_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_rate_limiting(async_client, valid_user_id):
    payload = {"user_id": valid_user_id, "title": "Test Doc", "content": "Content"}

    # Create 3 documents (up to limit)
    for i in range(3):
        payload["content"] = f"Content {i}"  # Different content to avoid cache hit
        resp = await async_client.post("/api/v1/documents", json=payload)
        assert resp.status_code == 201

    # The 4th should fail with 429
    payload["content"] = "Content 4"
    resp = await async_client.post("/api/v1/documents", json=payload)
    assert resp.status_code == 429
    assert "Too many active documents" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_caching(async_client, valid_user_id):
    payload = {
        "user_id": valid_user_id,
        "title": "Cache Doc",
        "content": "Identical Content",
    }

    # First request
    resp1 = await async_client.post("/api/v1/documents", json=payload)
    assert resp1.status_code == 201
    doc1 = resp1.json()
    assert doc1["status"] == "queued"

    # Manually simulate worker completing it
    from app.services.redis_service import RedisService

    content_hash = RedisService.compute_hash(payload["content"])
    await redis_service.cache_summary(content_hash, "Cached Summary")

    # Also decrement active jobs since worker would have done it
    await redis_service.decrement_active_jobs(payload["user_id"])

    # Second request with identical content
    resp2 = await async_client.post("/api/v1/documents", json=payload)
    assert resp2.status_code == 201
    doc2 = resp2.json()

    # Should be immediately completed with summary
    assert doc2["status"] == "completed"
    assert doc2["summary"] == "Cached Summary"

    # The IDs should be different (we create a new record for history)
    assert doc1["id"] != doc2["id"]
