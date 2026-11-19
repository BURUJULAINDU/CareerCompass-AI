"""Runs all executable tests and writes docs/test_results.md with REAL results.

Usage (from the project root):  python tests/run_tests.py
Tests that need packages or modules that are not present are listed as NOT EXECUTED.
"""
import datetime, platform, sys, time, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import conftest_path  # noqa: F401


class Collector(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.rows = []

    def _add(self, test, status, note=""):
        self.rows.append((test.id().split("tests.")[-1], test.shortDescription() or "", status, note))

    def addSuccess(self, test): super().addSuccess(test); self._add(test, "PASS")
    def addFailure(self, test, err): super().addFailure(test, err); self._add(test, "FAIL", str(err[1])[:120])
    def addError(self, test, err): super().addError(test, err); self._add(test, "ERROR", str(err[1])[:120])
    def addSkip(self, test, reason): super().addSkip(test, reason); self._add(test, "NOT EXECUTED", reason)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern="test_*.py")
    start = time.time()
    runner = unittest.TextTestRunner(resultclass=Collector, verbosity=1)
    result = runner.run(suite)
    counts = {}
    for _, _, s, _ in result.rows:
        counts[s] = counts.get(s, 0) + 1
    lines = [
        "# Test Execution Results",
        "",
        f"- Run on: {datetime.datetime.now():%Y-%m-%d %H:%M}",
        f"- Python: {platform.python_version()} on {platform.system()}",
        f"- Duration: {time.time() - start:.2f} s",
        f"- Summary: {counts}",
        "",
        "| Test | Status | Note |", "|---|---|---|",
    ]
    lines += [f"| {t} | {s} | {n} |" for t, _, s, n in sorted(result.rows)]
    out = ROOT / "docs" / "test_results.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nResults written to {out}")
    sys.exit(0 if result.wasSuccessful() else 1)
