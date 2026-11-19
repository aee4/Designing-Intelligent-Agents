"""Lab 2: a ReAct agent from scratch (no framework).

Usage (run from the repository root):
    python lab02/react_agent.py              # run the 6 test questions, save evidence/trace_1..6.txt
    python lab02/react_agent.py "question"   # run one question (trace printed only)
    python lab02/react_agent.py --baseline   # Step 1: model alone, writes evidence/baseline.md
"""
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from litellm import BadRequestError, completion

from tools import TOOLS

load_dotenv()
MODEL = os.getenv("LLM_MODEL")
EVIDENCE = Path(__file__).parent / "evidence"

SYSTEM_PROMPT = """You are a helpful assistant for a trader at Makola Market in Accra.
You answer costing questions and quick factual questions.

You can use these tools:
- calculator: evaluates an arithmetic expression, e.g. 4*185 + 3*95. Use it for ALL arithmetic.
- wiki_lookup: returns the summary of a Wikipedia page. The input is the page title, e.g. Bono East Region.
- finish: ends the task. The input is your final answer to the user.

You do NOT have function calling. Never call a tool directly; instead write the
action as plain text. Our code reads your text and runs the tool for you.

On every step reply in exactly this plain-text format and nothing else:
Thought: <your reasoning>
Action: calculator | wiki_lookup | finish
Action Input: <input for the tool, or the final answer if finish>

Rules:
- Use only one Action per reply, then stop. Never write an Observation yourself.
- Never do arithmetic in your head; always use the calculator.
- If a tool gives an error or no result, say so honestly instead of guessing.
- If no tool is needed, use finish straight away."""

ACTION_RE = re.compile(r"Action:\s*(\w+)\s*\nAction Input:\s*(.*)", re.DOTALL)

FORMAT_HELP = ("Your reply could not be parsed. Reply in exactly this format:\n"
               "Thought: <your reasoning>\nAction: calculator | wiki_lookup | finish\n"
               "Action Input: <input>")


def parse(text):
    m = ACTION_RE.search(text)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


def call_model(messages):
    try:
        resp = completion(model=MODEL, messages=messages,
                          temperature=0, stop=["Observation:"])
        return (resp.choices[0].message.content or "").strip()
    except BadRequestError as e:
        # gpt-oss sometimes tries a native function call instead of writing text.
        # Groq rejects it but returns the attempted call in the error, so we
        # rewrite that call in our text protocol and carry on.
        m = re.search(r'\{"error".*\}', str(e))
        if not m or "tool_use_failed" not in m.group(0):
            raise
        call = json.loads(json.loads(m.group(0))["error"]["failed_generation"])
        args = call.get("arguments") or {}
        value = next(iter(args.values()), "") if isinstance(args, dict) else args
        return (f"Thought: (model tried a native function call; converted to text)\n"
                f"Action: {call.get('name')}\nAction Input: {value}")


def run_agent(question, max_steps=6):
    """Run the Thought -> Action -> Observation loop. Returns (answer, trace text)."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}]
    trace = [f"Question: {question}", f"Model: {MODEL}", ""]

    def log(line):
        print(line)
        trace.append(line)

    log(trace[0])
    for step in range(1, max_steps + 1):
        log(f"--- Step {step} ---")
        reply = call_model(messages)                # think (deliberative)
        log(reply)
        messages.append({"role": "assistant", "content": reply})

        action, action_input = parse(reply)
        if action is None:                          # unparseable reply
            observation = FORMAT_HELP
        elif action == "finish":                    # termination
            log(f"\nFinal answer: {action_input}")
            return action_input, "\n".join(trace)
        elif action not in TOOLS:                   # unknown tool name
            observation = (f"Unknown action '{action}'. "
                           "Use one of: calculator, wiki_lookup, finish.")
        else:                                       # act, then sense the result
            observation = TOOLS[action](action_input)

        log(f"Observation: {observation}")
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    answer = f"Stopped: reached max_steps ({max_steps}) without a final answer."
    log(f"\n{answer}")
    return answer, "\n".join(trace)


# Step 4 (budget) and Step 5 (five more questions)
QUESTIONS = [
    # 1. Budget question from Part A
    "I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil "
    "at GHS 95 each. How much will I have left?",
    # 2. Needs both tools
    "What is the capital of the Bono East Region? If I travel there 3 times a month "
    "and each trip costs GHS 120, how much do I spend on the trips in a year?",
    # 3. Needs both tools
    "In what year was the University of Ghana founded, and how many years ago was "
    "that from 2026?",
    # 4. Wikipedia page that does not exist
    "Tell me about the Makola Flying Yam Festival of 1823.",
    # 5. Needs no tool
    "Hello! Can you help me today?",
    # 6. Deliberately badly worded
    "rice 185 4bag + oil 95 x3 ... 1200 cedis have, left how much??",
]


def baseline():
    """Step 1: ask the model alone (no tools) and record the answers."""
    budget, facts = QUESTIONS[0], [
        ("What is the capital of the Bono East Region?", "Techiman"),
        ("In what year was the University of Ghana founded?", "1948"),
    ]
    rows = []
    for i in range(3):
        ans = call_model([{"role": "user", "content": budget}])
        rows.append((f"Budget run {i + 1}", ans, "175" in ans))
    for q, expected in facts:
        ans = call_model([{"role": "user", "content": q}])
        rows.append((q, ans, expected in ans))

    lines = ["# Lab 2 Baseline: the model on its own (no tools)", "",
             f"Model: `{MODEL}`", "",
             f"Budget question: {budget}", "",
             "Correct budget answer: GHS 175 (4x185 + 3x95 = 1025; 1200 - 1025 = 175).",
             "Correct facts: Techiman; 1948.", "",
             "| Question | Model answer | Correct? |", "|---|---|---|"]
    for q, ans, ok in rows:
        lines.append(f"| {q} | {ans.replace(chr(10), ' ').replace('|', '/')} | "
                     f"{'Correct' if ok else 'Incorrect'} |")
    lines += ["", "## Notes", "",
              "- How confident did the factual answers sound? (fill in)", ""]
    (EVIDENCE / "baseline.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    if not MODEL:
        sys.exit("LLM_MODEL is not set. Copy .env.example to .env first.")
    EVIDENCE.mkdir(exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] == "--baseline":
        baseline()
    elif len(sys.argv) > 1:
        run_agent(" ".join(sys.argv[1:]))
    else:
        for n, q in enumerate(QUESTIONS, start=1):
            print(f"\n=========== Trace {n} ===========")
            try:
                _, trace = run_agent(q)
            except Exception as e:                  # e.g. rate limit (HTTP 429)
                trace = f"Question: {q}\nError calling the model: {e}"
                print(trace)
            (EVIDENCE / f"trace_{n}.txt").write_text(trace, encoding="utf-8")
