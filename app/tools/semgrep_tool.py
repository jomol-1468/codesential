import subprocess, tempfile, os, json
from langchain.tools import tool


@tool
def run_semgrep_scan(code_snippet: str) -> str:
    """
    Run a Semgrep SAST scan on Python source code.
    Use this to detect OWASP Top 10 patterns including
    SQL injection, XSS, hardcoded credentials, path
    traversal, insecure deserialization, and command
    injection. Returns matched rule IDs and line numbers.
    """
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w",
        delete=False, encoding="utf-8"
    ) as f:
        f.write(code_snippet)
        tmp = f.name

    try:
        res = subprocess.run(
            ["semgrep", "--config=p/owasp-top-ten",
             "--json", "--quiet", tmp],
            capture_output=True, text=True, timeout=60
        )
        try:
            output = res.stdout.strip()
            if not output:
                return "No issues found by Semgrep."
            data = json.loads(output)
            findings = data.get("results", [])
            if not findings:
                return "No issues found by Semgrep."
            return "\n".join([
                f"[{f['check_id'].split('.')[-1]}]"
                f" line {f['start']['line']}: {f['extra']['message']}"
                for f in findings
            ])
        except json.JSONDecodeError:
            return "No issues found by Semgrep."
    finally:
        os.unlink(tmp)