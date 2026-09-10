"""Pinned protocol values used by the pre-testnet harness.

The FLOP Yellow Paper is still an iterating implementation specification.
These values are deliberately isolated here so a later spec/runtime change does
not leak through the rest of the agent.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ProtocolProfile:
    spec_version: str
    spec_updated: str
    source_url: str
    max_session_key_duration_blocks: int
    circuit_breaker_tx_count: int
    circuit_breaker_flop_cap: Decimal
    channel_max_settlement_turns: int


CURRENT_PROTOCOL = ProtocolProfile(
    spec_version="0.5.0-draft",
    spec_updated="2026-09-05",
    source_url="https://flop.finance/intro/yellowpaper/",
    max_session_key_duration_blocks=864_000,
    circuit_breaker_tx_count=100,
    circuit_breaker_flop_cap=Decimal("250"),
    channel_max_settlement_turns=1_024,
)
