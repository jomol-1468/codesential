import asyncio
from celery import Celery
from app.config import settings

celery_app = Celery(
    "codesentinel",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

BOT_MARKER = "<!-- codesentinel-bot -->"
HEADER = f"{BOT_MARKER}\n> **CodeSentinel AI Review**\n---\n"


def post_review(repo_name: str, pr_number: int, review: str):
    try:
        from github import Github, Auth
        from app.config import settings
        g = Github(auth=Auth.Token(settings.github_token))
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        for c in pr.get_issue_comments():
            if BOT_MARKER in c.body:
                c.edit(HEADER + review)
                return
        pr.create_issue_comment(HEADER + review)
    except Exception as e:
        print(f"Failed to post review: {e}")


@celery_app.task(bind=True, max_retries=3)
def review_pr_task(self, repo: str, pr_number: int):
    try:
        from app.agents.review_agent import run_code_review
        review = asyncio.run(
            run_code_review(repo, pr_number)
        )
        post_review(repo, pr_number, review)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)