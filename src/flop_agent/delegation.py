"""Fail-closed policy checks for delegated agent/session-key authority."""

from dataclasses import dataclass
from decimal import Decimal

from .protocol_profile import CURRENT_PROTOCOL, ProtocolProfile


class PolicyViolation(RuntimeError):
    """Raised when a delegated action would exceed its pre-authorized bounds."""


@dataclass(frozen=True, slots=True)
class DelegationPolicy:
    duration_blocks: int
    per_tx_cap_flop: Decimal
    daily_cap_flop: Decimal
    allowed_pallets: frozenset[str]
    allowed_destinations: frozenset[str] = frozenset()
    protocol: ProtocolProfile = CURRENT_PROTOCOL

    def __post_init__(self) -> None:
        if not 0 < self.duration_blocks <= self.protocol.max_session_key_duration_blocks:
            raise ValueError("session-key duration exceeds the protocol maximum")
        if self.per_tx_cap_flop <= 0 or self.daily_cap_flop <= 0:
            raise ValueError("spend caps must be positive")
        if self.per_tx_cap_flop > self.daily_cap_flop:
            raise ValueError("per-tx cap cannot exceed daily cap")
        if not self.allowed_pallets:
            raise ValueError("at least one pallet must be explicitly allowlisted")

    def authorize(
        self,
        *,
        pallet: str,
        destination: str | None,
        amount_flop: Decimal,
        daily_spent_flop: Decimal,
        window_tx_count: int,
        window_spent_flop: Decimal,
    ) -> None:
        if pallet not in self.allowed_pallets:
            raise PolicyViolation("pallet is not allowlisted")
        if self.allowed_destinations and destination not in self.allowed_destinations:
            raise PolicyViolation("destination is not allowlisted")
        if amount_flop <= 0:
            raise PolicyViolation("spend amount must be positive")
        if amount_flop > self.per_tx_cap_flop:
            raise PolicyViolation("per-transaction cap exceeded")
        if daily_spent_flop + amount_flop > self.daily_cap_flop:
            raise PolicyViolation("daily cap exceeded")
        if window_tx_count + 1 > self.protocol.circuit_breaker_tx_count:
            raise PolicyViolation("circuit-breaker transaction count exceeded")
        if window_spent_flop + amount_flop > self.protocol.circuit_breaker_flop_cap:
            raise PolicyViolation("circuit-breaker spend cap exceeded")
