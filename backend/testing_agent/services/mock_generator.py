
import ast


def generate_tests(source_code):
    """Generate basic independent tests for supported arithmetic functions."""

    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        raise ValueError(
            f"Invalid Python syntax: {exc.msg}"
        ) from exc

    if len(tree.body) != 1 or not isinstance(
        tree.body[0], ast.FunctionDef
    ):
        raise ValueError("Mock mode supports one function only.")

    function = tree.body[0]

    if len(function.args.args) != 2 or function.args.defaults:
        raise ValueError(
            "Function must have exactly two required parameters."
        )

    if (
        function.decorator_list
        or function.args.vararg
        or function.args.kwarg
        or function.args.kwonlyargs
    ):
        raise ValueError("Unsupported function arguments.")

    if len(function.body) != 1 or not isinstance(
        function.body[0], ast.Return
    ):
        raise ValueError("Function must contain one return statement.")

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

    names = {arg.arg for arg in function.args.args}
    left, right = expression.left, expression.right

    if not (
        isinstance(left, ast.Name)
        and isinstance(right, ast.Name)
        and {left.id, right.id} == names
    ):
        raise ValueError(
            "Use both parameters directly in the arithmetic expression."
        )

    # IMPORTANT:
    # This prototype only generates expected results for the detected
    # operation. It cannot reliably detect a semantic bug such as
    # subtraction mistakenly used in a function named add.
    a, b = [arg.arg for arg in function.args.args]

    cases = [
        ("positive_values", 10, 2),
        ("negative_values", -10, 2),
        ("zero_first_argument", 0, 2),
    ]

    if isinstance(expression.op, (ast.Div, ast.FloorDiv, ast.Mod)):
        cases.append(("zero_second_argument", 10, 0))

    tests = []

    for name, x, y in cases:
        if isinstance(expression.op, ast.Add):
            expected = x + y
        elif isinstance(expression.op, ast.Sub):
            expected = x - y
        elif isinstance(expression.op, ast.Mult):
            expected = x * y
        elif isinstance(expression.op, ast.Div):
            expected = None if y == 0 else x / y
        elif isinstance(expression.op, ast.FloorDiv):
            expected = None if y == 0 else x // y
        elif isinstance(expression.op, ast.Mod):
            expected = None if y == 0 else x % y
        else:
            raise ValueError("Unsupported arithmetic operation.")

        tests.append({
            "name": name,
            "input": {a: x, b: y},
            "expected": expected,
            "expect_error": expected is None,
        })

    return {
        "function_name": function.name,
        "tests": tests,
    }
