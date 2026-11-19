# Lab 2: Architectures: A ReAct Agent From Scratch: Concept Check

Answer in your own words before the Wednesday session (independent work). Your answers feed Section 2 of your lab report (Concept and classical root).

## Q1. Classify a thermostat, a chess engine and a ReAct agent as reactive, deliberative or hybrid, with one reason each.

_Your answer:_

- **Thermostat: reactive.** It uses one condition-action rule ("if the temperature is below the set point, turn the heating on") on the current reading. It keeps no model of the world and does not plan.
- **Chess engine: deliberative.** It keeps an internal model of the board and searches many moves ahead to build a plan before it moves.
- **ReAct agent: hybrid.** The Thought step is deliberative (it plans what to do next across steps). Each Action reacts to the latest Observation, and the code around it reacts with fixed rules (run the named tool, send back a format error, stop at max_steps).

## Q2. In the trace above, which lines are percepts, and which are actions?

_Your answer:_

- **Percepts:** the user's question and the two `Observation:` lines (`Observation: 1025` and `Observation: 175`). These are what the agent senses from its environment.
- **Actions:** the `Action:` / `Action Input:` pairs: `calculator` with `4*185 + 3*95`, `calculator` with `1200 - 1025`, and `finish` with "You will have GHS 175 left." The finish action is the final reply to the user.
- The `Thought:` lines are neither. They are the agent's internal reasoning (the deliberation between percept and action).

## Q3. Why do we pass `stop=["Observation:"]` when calling the model?

_Your answer:_

The model is trained to continue text, so after writing an Action it would happily write its own `Observation:` line and invent the tool result (for example a wrong total). The stop sequence cuts the reply off at that word, so the model must hand control back to our code. Our code then runs the real tool and adds the real Observation. This keeps the percepts true and stops the model from pretending it used a tool.

## Q4. Map the trace above to the BDI terms belief, desire and intention.

_Your answer:_

- **Belief:** what the agent holds true so far: the question (budget GHS 1,200, 4 bags at GHS 185, 3 gallons at GHS 95) and the observations it received (total cost is 1025, then 175 left). In the code this is the conversation (messages list).
- **Desire:** the goal: tell the trader how much money will be left after buying the goods.
- **Intention:** the plan it commits to in its Thoughts: "I need the total cost first", then "Now subtract the cost from the budget". Each Action is one step of executing that intention. After each Observation it updates its beliefs and picks the next step, which is the BDI cycle.
