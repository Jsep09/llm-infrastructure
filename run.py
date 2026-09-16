"""Cross-platform dev runner (macOS, Linux, Windows).

Usage:
    uv run run.py dev    # start gateway with hot reload on http://127.0.0.1:8000
    uv run run.py test   # run test suite; extra args are passed through to pytest
"""

import subprocess
import sys

COMMANDS = {
    "dev": ["-m", "uvicorn", "gateway.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
    "test": ["-m", "pytest", "gateway/tests", "-v"],
}


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "dev"
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}. Use one of: {', '.join(COMMANDS)}", file=sys.stderr)
        return 2

    # sys.executable = interpreter running this script, so it works in any venv on any OS.
    args = [sys.executable, *COMMANDS[cmd], *sys.argv[2:]]
    try:
        return subprocess.run(args).returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
