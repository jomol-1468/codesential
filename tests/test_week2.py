from app.tools.rag_tool import search_codebase_context
from app.tools.github_tool import get_pr_diff


def test_rag_tool_importable():
    assert search_codebase_context.name == "search_codebase_context"
    assert search_codebase_context.description is not None


def test_github_tool_importable():
    assert get_pr_diff.name == "get_pr_diff"
    assert get_pr_diff.description is not None


def test_rag_tool_returns_string():
    result = search_codebase_context.invoke("database connection")
    assert isinstance(result, str)
    assert len(result) > 0


def test_github_tool_invalid_repo():
    result = get_pr_diff.invoke({
        "repo_name": "fake/fakerepo123456",
        "pr_number": 1
    })
    assert "Error" in result or "No Python" in result