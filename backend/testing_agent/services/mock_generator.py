
import ast


def generate_tests(source_code):
    """Generate independent tests for common, clearly named arithmetic functions."""

    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        raise ValueError(
            f"Invalid Python syntax: {exc.msg}"
        ) from exc

    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("Local mode supports one function only.")

    function = tree.body[0]

    if (
        len(function.args.args) != 2
        or function.args.defaults
        or function.args.vararg
        or function.args.kwarg
        or function.args.kwonlyargs
        or function.decorator_list
    ):
        raise ValueError("Function must have exactly two required parameters.")

    if len(function.body) != 1 or not isinstance(function.body[0], ast.Return):
        raise ValueError("Local mode supports one return statement.")

    expression = function.body[0].value
    allowed = (
        ast.Module, ast.FunctionDef, ast.arguments, ast.arg,
        ast.Return, ast.BinOp, ast.Name, ast.Constant, ast.Add,
        ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
        ast.Load, ast.UnaryOp, ast.USub, ast.UAdd,
    )

    if any(not isinstance(node, allowed) for node in ast.walk(tree)):
        raise ValueError("Unsupported Python syntax.")

    if not isinstance(expression, ast.BinOp):
        raise ValueError("Return an arithmetic expression.")

    param_names = [arg.arg for arg in function.args.args]
    if not (
        isinstance(expression.left, ast.Name)
        and isinstance(expression.right, ast.Name)
        and {expression.left.id, expression.right.id} == set(param_names)
    ):
        raise ValueError("Use both parameters directly in the arithmetic expression.")

    # This local oracle relies on conventional function names.
    # Unknown names must use the LLM path instead.
    name = function.name.lower()
    if name in {"add", "addition", "sum_numbers"}:
        operation = "add"
    elif name in {"subtract", "sub", "difference"}:
        operation = "subtract"
    elif name in {"multiply", "mult", "product"}:
        operation = "multiply"
    elif name in {"divide", "division"}:
        operation = "divide"
    else:
        raise ValueError("Unknown function intent; use LLM test generation.")

    a_name, b_name = param_names
    cases = [
        ("positive_values", 10, 2),
        ("negative_values", -10, 2),
        ("zero_first_argument", 0, 2),
        ("both_negative", -10, -2),
    ]

    if operation == "divide":
        cases.extend([
            ("float_inputs", 7, 2),
            ("zero_second_argument", 10, 0),
        ])

    tests = []
    for test_name, a, b in cases:
        if operation == "add":
            expected = a + b
        elif operation == "subtract":
            expected = a - b
        elif operation == "multiply":
            expected = a * b
        else:
            expected = None if b == 0 else a / b

        tests.append({
            "name": test_name,
            "input": {a_name: a, b_name: b},
            "expected": expected,
            "expect_error": operation == "divide" and b == 0,
        })

    return {
        "function_name": function.name,
        "tests": tests,
    }
