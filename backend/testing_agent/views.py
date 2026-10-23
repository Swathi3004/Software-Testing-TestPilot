
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.mock_generator import generate_tests as generate_local_tests
from .services.test_runner import run_tests
from .services.llm_generator import (
    GeminiUnavailableError,
    generate_tests_with_llm,
    suggest_code_fix,
)


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
        return Response({"error": "Source code is required."}, status=400)

    if len(code) > 10000:
        return Response(
            {"error": "Source code must be 10,000 characters or less."},
            status=400,
        )

    try:
        try:
            generated = generate_local_tests(code)
            generated["analysis"] = "Generated using local arithmetic rules."
            mode = "local"
        except ValueError as local_error:
            if str(local_error).startswith("Invalid Python syntax:"):
                return Response({"error": str(local_error)}, status=400)

            generated = generate_tests_with_llm(code)
            mode = "gemini"

        execution = run_tests(code, generated)

        return Response({
            "status": "success",
            "message": "Tests generated and executed.",
            "mode": mode,
            "function_name": generated["function_name"],
            "analysis": generated.get("analysis", ""),
            "tests": generated["tests"],
            "results": execution["results"],
            "total": execution["total"],
            "passed": execution["passed"],
            "failed": execution["failed"],
        })

    except GeminiUnavailableError as exc:
        return Response({"error": str(exc)}, status=503)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)


@api_view(["POST"])
def suggest_fix(request):
    code = request.data.get("code", "")
    failed_results = request.data.get("failed_results", [])

    if not isinstance(code, str) or not code.strip():
        return Response({"error": "Source code is required."}, status=400)

    if len(code) > 10000:
        return Response({"error": "Source code is too long."}, status=400)

    if not isinstance(failed_results, list) or not failed_results:
        return Response(
            {"error": "Failed test results are required."},
            status=400,
        )

    if len(failed_results) > 30:
        return Response(
            {"error": "No more than 30 failed results are allowed."},
            status=400,
        )

    try:
        # Send only failed results to the LLM.
        failed_only = [
            result for result in failed_results
            if isinstance(result, dict)
            and result.get("status") == "failed"
        ]

        if not failed_only:
            return Response(
                {"error": "No failed tests were provided."},
                status=400,
            )

        suggestion = suggest_code_fix(code, failed_only)

        return Response({
            "status": "success",
            "message": "AI code suggestion generated. It has not been verified.",
            **suggestion,
        })

    except GeminiUnavailableError as exc:
        return Response({"error": str(exc)}, status=503)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
