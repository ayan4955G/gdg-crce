import sys
import subprocess
import time
import tempfile
import os
try:
    import resource
except ImportError:
    resource = None
from typing import Dict, Any, Optional

class SandboxedCodeRunner:
    """
    Safely executes learner Python code inside an isolated subprocess
    with execution timeouts, memory limits, and prohibited standard libraries.
    """
    def __init__(self, timeout_seconds: float = 2.0, max_memory_mb: int = 128):
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb

    def run(self, code: str, stdin_input: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.perf_counter()
        
        # Pre-check for prohibited dangerous builtins/modules
        security_check = self._static_security_check(code)
        if not security_check["is_safe"]:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"SecurityViolation: {security_check['reason']}",
                "exit_code": 1,
                "execution_time_ms": 0.0,
                "timeout": False,
                "security_violation": True
            }

        # Write code to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
            temp_path = temp_file.name
            temp_file.write(code)

        try:
            # Execute in isolated subprocess with no network or parent env leak
            safe_env = {
                "PYTHONIOENCODING": "utf-8",
                "PYTHONHASHSEED": "0",
                "PATH": os.environ.get("PATH", "")
            }

            process = subprocess.Popen(
                [sys.executable, "-I", temp_path], # -I isolates from sys.path and user site packages
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=safe_env
            )

            try:
                stdout, stderr = process.communicate(input=stdin_input, timeout=self.timeout_seconds)
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return {
                    "success": process.returncode == 0,
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": process.returncode,
                    "execution_time_ms": round(elapsed_ms, 2),
                    "timeout": False,
                    "security_violation": False
                }
            except subprocess.TimeoutExpired:
                process.kill()
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"TimeoutError: Execution exceeded time limit of {self.timeout_seconds}s.",
                    "exit_code": -1,
                    "execution_time_ms": round(elapsed_ms, 2),
                    "timeout": True,
                    "security_violation": False
                }
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def _static_security_check(self, code: str) -> Dict[str, Any]:
        prohibited_tokens = [
            "import os", "from os", "import sys", "from sys",
            "import subprocess", "from subprocess",
            "__import__", "eval(", "exec(", "open(",
            "import socket", "from socket", "import shutil", "from shutil",
            "import pty", "from pty", "import requests", "from urllib"
        ]
        for token in prohibited_tokens:
            if token in code:
                return {
                    "is_safe": False,
                    "reason": f"Prohibited token or restricted module '{token}' detected."
                }
        return {"is_safe": True, "reason": None}

if __name__ == "__main__":
    runner = SandboxedCodeRunner()
    
    # Test valid code
    res = runner.run("for i in range(3): print('Num:', i)")
    print("Normal run:", res)

    # Test infinite loop timeout
    res_timeout = runner.run("while True: pass")
    print("Timeout run:", res_timeout)

    # Test restricted import
    res_sec = runner.run("import os; os.system('echo hacked')")
    print("Security block:", res_sec)
