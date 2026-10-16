"""Canonical data model. Every source file is normalised into these shapes."""

from __future__ import annotations

import hashlib
import re
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

#: Accounting period, e.g. "2026-09". Use with ``fullmatch``.
PERIOD_RE = re.compile(r"\d{4}-(0[1-9]|1[0-2])")

#: Tables the LLM is allowed to query. Anything else is rejected by the SQL guard.
ALLOWED_TABLES: frozenset[str] = frozenset({"transactions", "budget"})

#: Schema shown to the model in prompts. Kept short on purpose: small models do
#: better with a compact, unambiguous schema than with a full DDL dump.
SCHEMA_PROMPT = """\
TABLE transactions(
  id TEXT PRIMARY KEY,          -- stable hash of the source row
  source TEXT,                  -- 'gl' (general ledger) or 'bank'
  txn_date DATE,                -- ISO yyyy-mm-dd
  period TEXT,                  -- yyyy-mm, derived from txn_date
  account TEXT,                 -- GL account code or bank account alias
  account_name TEXT,
  category TEXT,                -- e.g. Revenue, COGS, Opex, Payroll, Tax
  counterparty TEXT,
  description TEXT,             -- PII-redacted free text
  amount_minor INTEGER,         -- signed amount in minor units (pence/cents); income > 0
  currency TEXT                 -- ISO-4217, e.g. GBP
)
TABLE budget(
  period TEXT, account TEXT, category TEXT, amount_minor INTEGER, currency TEXT
)
Notes: money is stored in minor units. Divide amount_minor by 100.0 for display.
"""


class Transaction(BaseModel):
    """One normalised ledger or bank line."""

    source: str = Field(pattern=r"^(gl|bank)$")
    txn_date: date
    account: str = Field(min_length=1, max_length=64)
    account_name: str = ""
    category: str = "Uncategorised"
    counterparty: str = ""
    description: str = ""
    amount: Decimal
    currency: str = Field(default="GBP", pattern=r"^[A-Z]{3}$")

    @field_validator("amount")
    @classmethod
    def _two_dp(cls, v: Decimal) -> Decimal:
        if v != v.quantize(Decimal("0.01")):
            raise ValueError(f"amount {v} has more than 2 decimal places")
        return v

    @property
    def period(self) -> str:
        return self.txn_date.strftime("%Y-%m")

    @property
    def amount_minor(self) -> int:
        return int(self.amount * 100)

    def row_id(self, row_index: int, file_digest: str) -> str:
        """Deterministic id: re-ingesting the same file is idempotent."""
        key = "|".join(
            [
                file_digest,
                str(row_index),
                self.source,
                self.txn_date.isoformat(),
                self.account,
                str(self.amount),
                self.currency,
            ]
        )
        return hashlib.sha256(key.encode()).hexdigest()[:32]


class BudgetLine(BaseModel):
    period: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    account: str
    category: str = "Uncategorised"
    amount: Decimal
    currency: str = Field(default="GBP", pattern=r"^[A-Z]{3}$")
