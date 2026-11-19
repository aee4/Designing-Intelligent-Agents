# Lab 2 Baseline: the model on its own (no tools)

Model: `groq/openai/gpt-oss-20b`

Budget question: I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at GHS 95 each. How much will I have left?

Correct budget answer: GHS 175 (4x185 + 3x95 = 1025; 1200 - 1025 = 175).
Correct facts: Techiman; 1948.

| Question | Model answer | Correct? |
|---|---|---|
| Budget run 1 | First, calculate the total cost of each item:  - **Rice:** 4 bags × GHS 185 = **GHS 740**   - **Oil:** 3 gallons × GHS 95 = **GHS 285**  Add them together to find the total expenditure:  GHS 740 + GHS 285 = **GHS 1,025**  Subtract this from your initial amount:  GHS 1,200 – GHS 1,025 = **GHS 175**  So you will have **GHS 175** left. | Correct |
| Budget run 2 | First, calculate the total cost of each item:  - **Rice:** 4 bags × GHS 185 = **GHS 740**   - **Oil:** 3 gallons × GHS 95 = **GHS 285**  Add them together to find the total expenditure:  GHS 740 + GHS 285 = **GHS 1,025**  Subtract this from your initial amount:  GHS 1,200 – GHS 1,025 = **GHS 175**  So you will have **GHS 175** left. | Correct |
| Budget run 3 | First, calculate the total cost of each item:  - **Rice:** 4 bags × GHS 185 = **GHS 740**   - **Oil:** 3 gallons × GHS 95 = **GHS 285**  Add them together to find the total expenditure:  GHS 740 + GHS 285 = **GHS 1,025**  Subtract this from your initial amount:  GHS 1,200 – GHS 1,025 = **GHS 175**  So you will have **GHS 175** left. | Correct |
| What is the capital of the Bono East Region? | The capital of the Bono East Region is **Techiman**. | Correct |
| In what year was the University of Ghana founded? | The University of Ghana was founded in **1948** (as the University College of Gold Coast). | Correct |

## Notes

- With temperature 0 all three budget runs gave the same, correct answer (GHS 175).
- Both factual answers were stated with full confidence and no hedging. They happened to be right, but the model would sound the same if it were wrong, and there is no source to check against. In the ReAct traces, the calculator and Wikipedia make each step checkable.
