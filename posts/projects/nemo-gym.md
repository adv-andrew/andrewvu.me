---
title: "Teaching an Agent to Run a 5G Network"
summary: "A reinforcement learning environment I built at NVIDIA, now merged into NeMo Gym"
order: 0
---

When a cell tower gets congested, a human operator decides what to reconfigure. During my Summer 2026 internship at NVIDIA, I worked on whether a language model could learn to make those calls instead.

## The setup

Most of the work wasn't the model, it was the world the model lives in. I built a stateful 5G environment where an agent sees the current cell KPIs, picks exactly one of eight bounded network-control commands, and gets scored on whether the network actually got better.

The scoring is the interesting part. There's no LLM judge anywhere in the loop. The environment validates the action, applies a deterministic state transition, measures the new KPIs, and computes a decomposed reward from the result. The reward function *is* the verifier, which means the agent can't talk its way to a good score.

## Training

I owned the post-training pipeline end to end. Supervised fine-tuning on Qwen3 first to teach the tool-calling format, then GRPO on synthetic traffic data I generated so the agent could learn on realistic congestion without touching anything real.

The clearest result: valid network commands went from 49% to 99.3%. Before GRPO the model was picking an invalid action about half the time.

## The part I actually learned from

I also built the evaluation harness, which scored four baselines — no-op, a scripted expert, SFT, and GRPO — on identical held-out scenarios.

It's the least glamorous thing I built and the most useful. A training run that finishes is not the same as a policy that works, and the harness was the thing that could tell me my own model wasn't good enough yet. It caught a failure mode I would otherwise have shipped and changed the next step from "run more training" to "fix tool-call reliability."

## Where it ended up

The environment merged into [NVIDIA NeMo Gym](https://github.com/NVIDIA-NeMo/Gym/pull/2564), the open-source framework NVIDIA uses to train and evaluate agents. I also wrote a [smaller runnable tutorial](https://github.com/NVIDIA/GenerativeAIExamples/pull/441) for GenerativeAIExamples so someone can follow the loop without a GPU or a 5G lab.

The reviewer called it "an unusually disciplined contribution," which I'm choosing to frame.

## Tech

- Python, PyTorch, Hugging Face
- NeMo Gym, NeMo RL
- SFT, GRPO, reward design
- Deterministic synthetic replay
