"""Spec-shaped inference session state machine.

This module models the agent-side safety boundary only. It intentionally does
not encode SCALE payloads, call RPC endpoints, or guess unpublished testnet
addresses.
"""

from dataclasses import dataclass
from enum import Enum, auto

from .ports import ReceiptSigner, TranscriptVerifier


class SessionState(Enum):
    IDLE = auto()
    OPENING = auto()
    OPEN = auto()
    STREAMING = auto()
    SETTLEMENT_PENDING = auto()
    SETTLED = auto()
    FAILED = auto()


@dataclass(frozen=True, slots=True)
class TurnReceipt:
    channel_id: str
    session_id: str
    turn_index: int
    input_hash: str
    output_hash: str
    cumulative_root: str
    aggregate_gn: int
    miner_signature: bytes

    def __post_init__(self) -> None:
        if self.turn_index < 0:
            raise ValueError("turn_index must be non-negative")
        if self.aggregate_gn < 0:
            raise ValueError("aggregate_gn must be non-negative")


class SessionController:
    """Enforces the safe agent-side lifecycle around a compute channel."""

    def __init__(self, verifier: TranscriptVerifier, signer: ReceiptSigner) -> None:
        self._verifier = verifier
        self._signer = signer
        self.state = SessionState.IDLE
        self.channel_id: str | None = None
        self.session_id: str | None = None
        self.last_turn_index: int | None = None
        self.last_cumulative_root: str | None = None
        self.aggregate_gn = 0

    def request_open(self) -> None:
        self._require(SessionState.IDLE)
        self.state = SessionState.OPENING

    def mark_open(self, channel_id: str, session_id: str) -> None:
        self._require(SessionState.OPENING)
        if not channel_id or not session_id:
            raise ValueError("channel_id and session_id are required")
        self.channel_id = channel_id
        self.session_id = session_id
        self.state = SessionState.OPEN

    def accept_turn(self, receipt: TurnReceipt) -> bytes:
        self._require(SessionState.OPEN, SessionState.STREAMING)
        if receipt.channel_id != self.channel_id or receipt.session_id != self.session_id:
            raise ValueError("receipt is bound to a different channel/session")

        expected = 0 if self.last_turn_index is None else self.last_turn_index + 1
        if receipt.turn_index != expected:
            raise ValueError(f"expected turn_index {expected}, got {receipt.turn_index}")
        if receipt.aggregate_gn < self.aggregate_gn:
            raise ValueError("aggregate_gn must be monotonic")

        if not self._verifier.verify_turn(receipt):
            self.state = SessionState.FAILED
            raise ValueError("miner turn verification failed")

        # The agent counter-signs only after verification. Callers should not
        # release/accept the output before this method succeeds.
        signature = self._signer.sign_receipt(receipt)
        if not signature:
            self.state = SessionState.FAILED
            raise ValueError("agent receipt signature is empty")

        self.last_turn_index = receipt.turn_index
        self.last_cumulative_root = receipt.cumulative_root
        self.aggregate_gn = receipt.aggregate_gn
        self.state = SessionState.STREAMING
        return signature

    def request_settlement(self) -> None:
        self._require(SessionState.STREAMING)
        if self.last_cumulative_root is None:
            raise RuntimeError("cannot settle without a verified receipt")
        self.state = SessionState.SETTLEMENT_PENDING

    def mark_settled(self) -> None:
        self._require(SessionState.SETTLEMENT_PENDING)
        self.state = SessionState.SETTLED

    def fail(self) -> None:
        if self.state is SessionState.SETTLED:
            raise RuntimeError("a settled session cannot transition to failed")
        self.state = SessionState.FAILED

    def _require(self, *allowed: SessionState) -> None:
        if self.state not in allowed:
            names = ", ".join(state.name for state in allowed)
            raise RuntimeError(f"state {self.state.name} not in allowed states: {names}")
