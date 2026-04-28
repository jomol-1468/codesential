import subprocess, tempfile, os, json, sys
from langchain.tools import tool
import shutil


@tool
def run_bandit_scan(code_snippet: str) -> str:
    """
    Run a Bandit SAST security scan on Python source code.
    Use this to detect SQL injection (B608), hardcoded
    passwords (B105/B106), eval/exec usage (B307), shell
    injection (B602), and insecure random numbers (B311).
    Returns a summary of findings with severity and line numbers.
    """
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w",
        delete=False, encoding="utf-8"
    ) as f:
        f.write(code_snippet)
        tmp = f.name

    try:
        # Find bandit executable path directly
        bandit_path = shutil.which("bandit")
        if not bandit_path:
            # Fallback to venv Scripts folder
            bandit_path = os.path.join(
                os.path.dirname(sys.executable), "bandit"
            )

        res = subprocess.run(
            [bandit_path, "-f", "json", "-l", "-i", tmp],
            capture_output=True, text=True, timeout=30
        )

        raw = res.stdout.strip()
        if not raw:
            raw = res.stderr.strip()
        if not raw:
            return "No security issues found by Bandit."

        try:
            data = json.loads(raw)
            items = data.get("results", [])
            if not items:
                return "No security issues found by Bandit."
            return "\n".join([
                f"[{r['issue_severity']}] {r['test_id']}: "
                f"{r['issue_text']} (line {r['line_number']})"
                for r in items
            ])
        except json.JSONDecodeError:
            return raw[:300]

    finally:
        os.unlink(tmp)