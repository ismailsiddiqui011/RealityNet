# RealityNet
## Hallucination Detection via Multi-Agent LLM Debate System

## Overview
This project implements a multi-agent architecture for detecting hallucination in LLM-generated outputs.
The system uses Verifier, Debator, Summarizer, and Judge agents to analyze generated content critically and assign a final Real/Fake probability score.

## Key Highlights
- Multi-Agent Self-Verification Chain (Inspired by Constitutional AI and Self-Reflection AI techniques)

- Modular Agents: Each agent specializes in factual checking, logical debating, summarizing inconsistencies, or judging final authenticity.

- Controlled Hallucination Generation: Main LLM instructed to fake some outputs for testing.

- Final Judgment: Clean probability scores like Real: 25%, Fake: 75%, no extra explanation.

- Lightweight Model Support: Optimized to run on 12GB VRAM setups.

- Fast Prototyping: Easily switch models or extend the debate chain.


## Model Setup (Ollama)
For Main LLM but you can use any model: 
```bash
ollama run llama3.2:3b
```
For Verifier, Debator and Judge but you can use any model(s) for each module:
```bash 
ollama run gemma3:4b
```

## How it Works
1- Generate: Main LLM creates the answer (real or hallucinated).

2- Verify: Verifier agent checks factual correctness.

3- Debate: Debator agent critiques logical consistency.

4- Summarize: Summarizer agent highlights potential errors.

5- Judge: Judge agent outputs final Real: xx% and Fake: xx% probability scores.

## Runner Code:
```python
from RealityNet import RealityNet
judge = RealityNet()
llm_answer, prob_score, verdict = judge.judge_flow('India got independence in 2014')
print(f'LLM answer : \n{llm_answer}')
print('---'*25)
print(f'Probability Score : \n{prob_score}')
print('---'*25)
print(f'Final Verdict : \n{verdict}')
```

