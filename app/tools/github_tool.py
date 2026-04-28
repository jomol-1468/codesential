from github import Github
from langchain.tools import tool
from app.config import settings

g = Github(settings.github_token)
SKIP_EXT = [".md", ".json", ".lock",
            ".txt", ".yml", ".yaml", ".toml"]


@tool
def get_pr_diff(repo_name: str, pr_number: int) -> str:
    """
    Fetch the code diff for a GitHub Pull Request.
    Returns only changed Python source files and their
    diffs. Use this as the first step in every code review.
    Args:
        repo_name: GitHub repo in owner/repo format
        pr_number: Pull request number as integer
    """
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        diffs = []
        for f in pr.get_files():
            if any(f.filename.endswith(s) for s in SKIP_EXT):
                continue
            diffs.append(
                f"=== {f.filename} ===\n{f.patch or ''}"
            )
        return "\n\n".join(diffs) if diffs \
            else "No Python files changed in this PR."
    except Exception as e:
        return f"Error fetching PR: {str(e)}"