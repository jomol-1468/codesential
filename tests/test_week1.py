from app.tools.bandit_tool import run_bandit_scan
from app.tools.semgrep_tool import run_semgrep_scan


def test_bandit_sql_injection():
    code = """
import sqlite3
conn = sqlite3.connect('db.sqlite')
conn.execute(f"SELECT * FROM users WHERE id={uid}")
"""
    result = run_bandit_scan.invoke(code)
    assert "B608" in result


def test_bandit_hardcoded_password():
    code = 'password = "admin123"'
    result = run_bandit_scan.invoke(code)
    assert "B105" in result


def test_bandit_eval():
    code = 'eval(input("code: "))'
    result = run_bandit_scan.invoke(code)
    assert "B307" in result


def test_semgrep_clean_code():
    code = """
def add(a: int, b: int) -> int:
    return a + b
"""
    result = run_semgrep_scan.invoke(code)
    assert "No issues" in result


def test_tools_importable():
    assert run_bandit_scan.name == "run_bandit_scan"
    assert run_semgrep_scan.name == "run_semgrep_scan"