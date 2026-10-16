# Security policy

## Threat model (summary)

| Threat | Control |
|---|---|
| Model-generated destructive SQL | Token guard (single SELECT, allow-listed tables) → read-only `mode=ro` connection → SQLite authorizer allow-list → progress-handler timeout |
| Prompt injection through ledger text | Planner never sees row data; narrator input is wrapped in `<result>` tags, declared untrusted and truncated to 80 chars per cell; narrator numbers must be grounded or the summary is replaced |
| PII leakage to prompts/logs | Redaction at ingest (email, IBAN, card w/ Luhn, sort code, account no., NINO, phone) |
| Spreadsheet formula injection on export | Leading `= + - @` neutralised at ingest |
| Unauthorised access | `X-API-Key` on all `/v1` routes, constant-time compare, fail-closed when unset; API bound to 127.0.0.1 |
| Tampering with evidence | SHA-256 hash-chained audit log with `flock` + `fsync` per entry (safe for API + CLI writers), `/v1/audit/verify` reports the first bad line |
| Server stalls / DoS | Blocking work off the event loop (threadpool); 10 s SQL timeout; LLM timeout; upload cap |
| Oversized uploads | 25 MB default cap (header and body checked) |
| Container breakout impact | Non-root user, read-only root FS, private network, model mounted read-only |

## Reporting

Please report vulnerabilities privately to the maintainers rather than opening a public issue.
Include reproduction steps and affected version. We aim to acknowledge within 3 working days.

## Known limitations (v0.1)

- Single shared API key; no per-user RBAC (planned v0.2).
- No built-in rate limiting — put the API behind a reverse proxy with limits.
- Pin the llama.cpp base image to a digest before production use.
