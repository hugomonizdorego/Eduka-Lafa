"""Bounded arithmetic for /calc. Parses with ast; never uses eval or exec."""
import ast
import math
import operator

class CalcError(ValueError): pass

BINARY = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
FUNCTIONS = {"sqrt": math.sqrt, "abs": abs, "round": round, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log10, "ln": math.log}
CONSTANTS = {"pi": math.pi, "e": math.e}

def calculate(expression):
    text = expression.strip().replace("×", "*").replace("÷", "/").replace("^", "**").replace(",", ".")
    if not 1 <= len(text) <= 200: raise CalcError("Enter a calculation of 1–200 characters, for example /calc (3+4)*2.")
    try: tree = ast.parse(text, mode="eval")
    except SyntaxError: raise CalcError("LAFA could not read this calculation. Use numbers, + - * / ^ and brackets.") from None
    if sum(1 for _ in ast.walk(tree)) > 120: raise CalcError("This calculation is too long.")
    try: value = evaluate(tree.body)
    except ZeroDivisionError: raise CalcError("Division by zero is undefined.") from None
    except (OverflowError, ValueError) as error:
        if isinstance(error, CalcError): raise
        raise CalcError("The result is outside LAFA's number range.") from None
    if isinstance(value, float):
        if not math.isfinite(value): raise CalcError("The result is outside LAFA's number range.")
        value = round(value, 10)
        if value.is_integer() and abs(value) < 1e15: value = int(value)
    return value

def evaluate(node):
    if isinstance(node, ast.Constant) and type(node.value) in {int, float}: return node.value
    if isinstance(node, ast.Name) and node.id in CONSTANTS: return CONSTANTS[node.id]
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY: return UNARY[type(node.op)](evaluate(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in BINARY:
        left, right = evaluate(node.left), evaluate(node.right)
        if isinstance(node.op, ast.Pow) and (abs(right) > 100 or abs(left) > 1e6): raise CalcError("Powers are limited to small numbers.")
        result = BINARY[type(node.op)](left, right)
        if isinstance(result, int) and abs(result) > 10**30: raise CalcError("The result is outside LAFA's number range.")
        return result
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS and not node.keywords and len(node.args) == 1:
        return FUNCTIONS[node.func.id](evaluate(node.args[0]))
    raise CalcError("Only numbers, + - * / ^ %, brackets, pi, e and sqrt/abs/round/sin/cos/tan/log/ln are allowed.")
