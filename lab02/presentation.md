# Lab 2 Presentation Script: A ReAct Agent From Scratch

## 1. What I built (30 sec)

"For Lab 2 I built a ReAct agent in plain Python, with no framework. It helps a trader at
Makola Market with costing questions and quick facts. It has two tools: a safe calculator
and a Wikipedia lookup."

Files:
- `tools.py`: the tools (the agent's actuators)
- `react_agent.py`: the prompt, parser and agent loop
- `concept_check.md`: theory answers
- `evidence/`: baseline, traces and a failure trace

## 2. The theory (1 min)

- **Reactive** agents map the current percept straight to an action (a thermostat).
- **Deliberative** agents keep a world model and plan before acting (a chess engine).
- **BDI**: Beliefs (what it knows), Desires (goals), Intentions (the plan it commits to).
- **Hybrid** agents mix both. **ReAct is a hybrid:**
  - **Thought** is deliberative: the model plans the next step.
  - **Action** calls a tool.
  - **Observation** is the new percept: the tool's result is fed back.
  - The loop repeats until the model chooses `finish`, or until `max_steps` is reached.

Key point: "The model never runs the tool. It only writes text naming the tool. My code
parses that text, runs the tool and sends back the result."

## 3. How it works (1 min)

1. The **system prompt** lists the tools and forces this format:
   ```
   Thought: <reasoning>
   Action: calculator | wiki_lookup | finish
   Action Input: <input>
   ```
2. I call the model with **`stop=["Observation:"]`**, so it cannot invent tool results.
3. A **regex parser** pulls out the Action and Action Input.
4. The code runs the tool and appends `Observation: <result>` to the conversation.
5. The loop repeats, up to **`max_steps=6`**.

**Safety:** the calculator uses Python's `ast` module, never `eval`.
`calculator("__import__('os')")` returns an error.

## 4. Live demo (2 min)

Run from the `Designing-Intelligent-Agents` folder:

```bash
python lab02/react_agent.py "I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at GHS 95 each. How much will I have left?"
```
Point out: Thought → `calculator` (4*185 + 3*95) → Observation 1025 → `calculator`
(1200 - 1025) → Observation 175 → `finish`. "The model decides **what** to compute; the code
computes."

Second demo, using Wikipedia:
```bash
python lab02/react_agent.py "What is the capital of the Bono East Region?"
```

## 5. Robustness: what happens when things go wrong (1 min)

The loop never crashes. It handles:
- **A reply it cannot parse:** sends back an Observation explaining the required format.
- **An unknown tool name:** sends back "Unknown action, use calculator, wiki_lookup or finish".
- **A Wikipedia page that doesn't exist:** the tool returns "No Wikipedia page found".
- **A runaway loop:** stops at `max_steps` with a clear message.

## 6. Baseline vs ReAct (30 sec)

- **Baseline (model alone, no tools):** 3 out of 3 budget answers were correct (GHS 175), and
  2 out of 2 facts were correct (Techiman; 1948). See `evidence/baseline.md`.
- "The model got these easy ones right on its own, but it sounds equally confident whether or
  not it is right. With ReAct, the arithmetic is done by real code and the facts come from a
  real source, so every answer can be checked in the trace."

## 7. Real failure and fix (1 min)

- **Failure:** on the first real run, every question crashed with
  `Tool choice is none, but model called a tool` (see `evidence/failure_native_tool_call.txt`).
- **Cause:** the model, `gpt-oss-20b`, is trained for native function calling. It saw tool
  names in the prompt and tried to call them as functions instead of writing `Action:` as text,
  and Groq rejected that call.
- **Fix attempt 1:** I told the model in the prompt not to use function calling. This **didn't
  work.**
- **Fix 2:** Groq's error contains the call the model attempted. My code turns it into
  `Action: <tool>` / `Action Input: <value>` and the loop carries on. This is reactive error
  handling: a fixed rule for a known failure.

## 8. Which parts are deliberative and which are reactive? (30 sec)

| Part | Type |
|---|---|
| The model's Thought (planning the next step) | Deliberative |
| Parsing the reply and running the named tool | Reactive |
| Format-error, unknown-tool and native-call handling | Reactive |
| The `max_steps` limit | Reactive (a safety rule) |

## 9. Closing line

"ReAct is a modern hybrid architecture: the model deliberates in its Thoughts, and the code
reacts to each Action with real tools and real observations. That makes the agent's answers
checkable instead of just confident."
