# Ironwise

Drop your finance spreadsheets in. Ask questions like a human. Get numbers you can actually trust — and prove where they came from.

**Self-hosted. Under 7 GB. Your data never leaves the box.**

```
$ ironwise ask "What was hosting cost in September?"
→ $5,805.31 (from the general ledger)
```

## What it does for you

- **Load ledgers, bank statements, and budgets** — CSV or Excel. It cleans columns, redacts sensitive bits, and stores everything as clean numbers.
- **Ask in plain English** — “What’s the P&L for September?”, “Where did we go over budget?”, “Does the bank match the books?”
- **Get real calculations, not guesses** — Every number comes from actual SQL or finance functions. The model never does the math.
- **Full audit trail** — Every question, every query, every answer is logged in a tamper-evident chain. Show an auditor exactly how a figure was produced.
- **Runs on one server you own** — No cloud analytics bill, no sending ledgers to someone else’s AI.

## Why this exists

Most “AI for finance” tools are hosted, consumption-priced, and black boxes. You can’t easily show how a number was calculated. Ironwise keeps the data on your machine and makes the calculation path obvious.

## Quick start

```bash
pip install -e ".[dev]"
export IRONWISE_API_KEY=change-me

# Load sample data (or your own CSVs)
ironwise ingest data/sample/gl_extract.csv --source gl
ironwise ingest data/sample/bank_statement.csv --source bank
ironwise ingest data/sample/budget.csv --source budget

# Run the built-in tools (no model required)
ironwise pnl --period 2026-09
ironwise variance --period 2026-09
ironwise reconcile --period 2026-09 --cash-account 1200
```

Want the natural-language layer? Drop a compatible 7–8B model GGUF into `models/` and start the stack with `docker compose` (see `deploy/`).

## What you get out of the box

| Thing | Utility |
|---|---|
| Ingest | Turn messy finance exports into a clean, queryable database |
| SQL guard | Model can only run safe, read-only queries |
| P&L / variance / reconcile | Deterministic finance tools you can trust |
| Audit log | Hash-chained record of every step |
| Size gate | Whole thing stays under 7 GB |

## Status

v0.1.1 — application, tests, evals, and pipeline are ready. The fine-tuned model weights are produced by the `training/` folder (~5 GB GGUF). Any OpenAI-compatible 7–8B instruction model works in the meantime.

## Repo map

- `ironwise/` — runtime (API, agent, ingest, store, finance tools, audit)
- `tests/` — 129 tests
- `evals/` — golden questions
- `training/` — LoRA fine-tune path
- `deploy/` — Docker setup
- `docs/` — market notes and technical spec

Config lives in `.env.example` (`IRONWISE_*` variables).

MIT. Base model (Qwen) is Apache-2.0.
