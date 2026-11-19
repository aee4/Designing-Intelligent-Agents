"""Lab 2 tools (the agent's actuators): a safe calculator and a Wikipedia lookup."""
import ast
import operator as op

import requests

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
       ast.Div: op.truediv, ast.USub: op.neg}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate arithmetic safely with the ast module (never eval)."""
    try:
        expr = expression.replace(",", "")
        return str(_eval(ast.parse(expr, mode="eval").body))
    except Exception as e:
        return f"Error: {e}"


def wiki_lookup(title: str) -> str:
    """Return the first 800 characters of a Wikipedia page summary."""
    url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
           + title.strip().replace(" ", "_"))
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "DCIT403-lab"})
    except requests.RequestException as e:
        return f"Error: could not reach Wikipedia ({e})."
    if r.status_code != 200:
        return f"No Wikipedia page found for '{title}'."
    return r.json().get("extract", "")[:800]


TOOLS = {"calculator": calculator, "wiki_lookup": wiki_lookup}


if __name__ == "__main__":
    # Step 2 checkpoint: test both tools directly before connecting the model.
    print("4*185 + 3*95 =", calculator("4*185 + 3*95"))
    print("1,200 - 1025 =", calculator("1,200 - 1025"))
    print("unsafe input  =", calculator("__import__('os')"))
    print("wiki:", wiki_lookup("Bono East Region")[:200])
    print("wiki missing:", wiki_lookup("Makola Flying Yam Festival"))
