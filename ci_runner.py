# ci_runner.py
import os; os.environ.setdefault("MOCK_MODE", "1")
import mocks
print("[Mock Mode] Enabling mock modules for CI/headless…")
mocks.enable()

# Now import your application normally
import sys
import main

if __name__ == "__main__":
    # pass through CLI flags like --mock --no-preflight
    sys.exit(main.main())
