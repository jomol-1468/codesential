import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException
from app.config import settings

app = FastAPI(title="CodeSentinel AI")


def verify_signature(body: bytes, sig: str) -> bool:
    secret = settings.webhook_secret.encode()
    expected = hmac.new(
        secret, body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(sig, f"sha256={expected}")


@app.post("/webhook/github")
async def github_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(body, sig):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    payload = await request.json()
    action = payload.get("action")

    if action in ("opened", "synchronize"):
        from app.tasks import review_pr_task
        task = review_pr_task.delay(
            payload["repository"]["full_name"],
            payload["number"],
        )
        return {"job_id": task.id, "status": "queued"}

    return {"status": "ignored", "action": action}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "CodeSentinel AI"}