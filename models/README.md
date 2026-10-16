# models/

Place the quantised model here. It is git-ignored and mounted read-only into the
`llm` container.

Expected file: `ironwise-8b-q4_k_m.gguf` (≈ 5.0–5.1 GB), produced by the pipeline in
[`training/README.md`](../training/README.md).

Until you have trained Ironwise, any instruction-tuned 7–8B GGUF works for evaluation
(set `IRONWISE_GGUF` in `.env`). Check the total stays within budget:

```bash
make size-check
```

Verify integrity before deploying and record the hash in your release notes:

```bash
sha256sum models/ironwise-8b-q4_k_m.gguf
```
