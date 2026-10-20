
import json
import subprocess
import sys
import tempfile


def run_tests(source_code, generated):
    """Run generated tests in a separate Python process.

    Note: This is a local prototype, not a secure sandbox
    for untrusted Python code.
    """

    payload = json.dumps(generated)

    runner_code = r'''
import json
import math
import sys
import traceback

separator = "\n# TEST_DATA_SEPARATOR\n"
raw = sys.stdin.read()

if separator not in raw:
    raise ValueError("Invalid test runner input.")

source, test_data = raw.split(separator, 1)
data = json.loads(test_data)

namespace = {"__builtins__": {}}
exec(compile(source, "<submitted-code>", "exec"), namespace)

function_name = data["function_name"]
function = namespace.get(function_name)

if not callable(function):
    raise ValueError("The requested function was not found.")

results = []

for test in data["tests"]:
    try:
        actual = function(**test["input"])

        if test.get("expect_error"):
            results.append({
                "name": test["name"],
                "status": "failed",
                "message": "Expected an exception, but none was raised."
            })
            continue

        expected = test.get("expected")

        if (
            isinstance(actual, (int, float))
            and not isinstance(actual, bool)
            and isinstance(expected, (int, float))
            and not isinstance(expected, bool)
        ):
            passed = math.isclose(
                actual, expected,
                rel_tol=1e-9,
                abs_tol=1e-9
            )
        else:
            passed = actual == expected

        results.append({
            "name": test["name"],
            "status": "passed" if passed else "failed",
            "expected": expected,
            "actual": (
                actual
                if isinstance(actual, (int, float, str, bool, type(None)))
                else repr(actual)
            ),
            "message": (
                "" if passed
                else "Actual result did not match expected result."
            )
        })

    except Exception as exc:
        expected_error = test.get("expect_error", False)
        passed = expected_error and type(exc).__name__ == "ZeroDivisionError"

        results.append({
            "name": test["name"],
            "status": "passed" if passed else "failed",
            "message": (
                "Expected ZeroDivisionError was raised."
                if passed
                else type(exc).__name__ + ": " + str(exc)
            )
        })

print(json.dumps(results))
'''

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            completed = subprocess.run(
                [sys.executable, "-I", "-c", runner_code],
                input=source_code + "\n# TEST_DATA_SEPARATOR\n" + payload,
                capture_output=True,
                text=True,
                timeout=5,
                cwd=temp_dir,
            )
    except subprocess.TimeoutExpired:
        raise ValueError("Test execution timed out.") from None

    if completed.returncode != 0:
        error_message = completed.stderr.strip()
        raise ValueError(
            error_message[-1000:]
            if error_message
            else "Test runner failed."
        )

    try:
        results = json.loads(completed.stdout)
    except json.JSONDecodeError:
        raise ValueError("Could not read test runner results.") from None

    passed = sum(item["status"] == "passed" for item in results)

    return {
        "results": results,
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
    }
