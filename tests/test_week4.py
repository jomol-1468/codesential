import hmac
import hashlib
from fastapi.testclient import TestClient
from app.api.webhook import app
from app.config import settings

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_webhook_rejects_no_signature():
    response = client.post(
        "/webhook/github",
        json={"action": "opened"}
    )
    assert response.status_code == 401


def test_webhook_rejects_wrong_signature():
    response = client.post(
        "/webhook/github",
        json={"action": "opened"},
        headers={"X-Hub-Signature-256": "sha256=wrongsig"}
    )
    assert response.status_code == 401


def make_valid_signature(body: bytes) -> str:
    secret = settings.webhook_secret.encode()
    sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


def test_webhook_ignores_non_pr_action():
    import json
    body = json.dumps({"action": "closed"}).encode()
    sig = make_valid_signature(body)
    response = client.post(
        "/webhook/github",
        content=body,
        headers={
            "X-Hub-Signature-256": sig,
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"


def test_tasks_importable():
    from app.tasks import celery_app, review_pr_task
    assert celery_app is not None
    assert review_pr_task is not None
    print("\nCelery app ready:", celery_app.main)