
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.llm_generator import generate_tests_with_llm
from .services.test_runner import run_tests


@api_view(["GET"])
def health_check(request):
    return Response({
        "status": "success",
        "message": "LLM Testing Agent API is running!"
    })


@api_view(["POST"])
def generate_tests(request):
    code = request.data.get("code", "")

    if not isinstance(code, str) or not code.strip():
        return Response(
            {"error": "Source code is required."},
            status=400
        )

    if len(code) > 10000:
        return Response(
            {"error": "Source code must be 10,000 characters or less."},
            status=400
        )

    try:
        generated = generate_tests_with_llm(code)

        # Validate the generated test structure before using it.
        tests = generated.get("tests", [])
        if not tests or len(tests) > 30:
            return Response(
                {"error": "AI returned an invalid number of tests."},
                status=400
            )

        for test in tests:
            if (
                not isinstance(test, dict)
                or not isinstance(test.get("name"), str)
                or not isinstance(test.get("input"), dict)
                or "expected" not in test
                or not isinstance(test.get("expect_error"), bool)
            ):
                return Response(
                    {"error": "AI returned an invalid test case."},
                    status=400
                )

        # Prototype only: this runner is not a secure sandbox.
        execution = run_tests(code, generated)

        return Response({
            "status": "success",
            "message": "AI tests generated and executed.",
            "mode": "gemini",
            "function_name": generated["function_name"],
            "analysis": generated.get("analysis", ""),
            "tests": tests,
            "results": execution["results"],
            "total": execution["total"],
            "passed": execution["passed"],
            "failed": execution["failed"],
        })

    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
