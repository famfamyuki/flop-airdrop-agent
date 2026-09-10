"""Boundary interfaces for cryptography and the not-yet-public testnet rail."""

from typing import Protocol


class NetworkNotConfigured(RuntimeError):
    """Raised when code tries to use a network binding before it is configured."""


class TranscriptVerifier(Protocol):
    def verify_turn(self, receipt: object) -> bool:
        """Verify the miner's signed turn/transcript material."""


class ReceiptSigner(Protocol):
    def sign_receipt(self, receipt: object) -> bytes:
        """Counter-sign a verified cumulative receipt."""


class FlopNetworkPort(Protocol):
    def claim_faucet(self) -> str: ...

    def open_channel(self, request: dict[str, object]) -> str: ...

    def settle(self, request: dict[str, object]) -> str: ...


class UnconfiguredFlopNetworkAdapter:
    """Fail-closed placeholder until official testnet endpoints are published."""

    @staticmethod
    def _blocked() -> None:
        raise NetworkNotConfigured(
            "FLOP Testnet network binding is intentionally disabled until official "
            "RPC/faucet/runtime details are published and verified."
        )

    def claim_faucet(self) -> str:
        self._blocked()
        raise AssertionError("unreachable")

    def open_channel(self, request: dict[str, object]) -> str:
        del request
        self._blocked()
        raise AssertionError("unreachable")

    def settle(self, request: dict[str, object]) -> str:
        del request
        self._blocked()
        raise AssertionError("unreachable")
