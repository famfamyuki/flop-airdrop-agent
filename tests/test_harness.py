import tempfile
import unittest
from pathlib import Path
from decimal import Decimal

from flop_agent.delegation import DelegationPolicy, PolicyViolation
from flop_agent.ledger import EvidenceLedger
from flop_agent.ports import NetworkNotConfigured, UnconfiguredFlopNetworkAdapter
from flop_agent.protocol_profile import CURRENT_PROTOCOL
from flop_agent.session import SessionController, SessionState, TurnReceipt


class AcceptAllVerifier:
    def verify_turn(self, receipt: object) -> bool:
        return True


class FakeSigner:
    def sign_receipt(self, receipt: object) -> bytes:
        return b"agent-signature"


class HarnessTests(unittest.TestCase):
    def make_controller(self) -> SessionController:
        return SessionController(AcceptAllVerifier(), FakeSigner())

    def test_protocol_profile_is_pinned(self) -> None:
        self.assertEqual(CURRENT_PROTOCOL.spec_version, "0.5.0-draft")
        self.assertEqual(CURRENT_PROTOCOL.max_session_key_duration_blocks, 864_000)

    def test_happy_path_requires_verified_receipt_before_settlement(self) -> None:
        controller = self.make_controller()
        controller.request_open()
        controller.mark_open("channel-1", "session-1")
        signature = controller.accept_turn(
            TurnReceipt(
                channel_id="channel-1",
                session_id="session-1",
                turn_index=0,
                input_hash="in",
                output_hash="out",
                cumulative_root="root",
                aggregate_gn=42,
                miner_signature=b"miner",
            )
        )
        self.assertEqual(signature, b"agent-signature")
        controller.request_settlement()
        controller.mark_settled()
        self.assertEqual(controller.state, SessionState.SETTLED)

    def test_non_monotonic_turn_is_rejected(self) -> None:
        controller = self.make_controller()
        controller.request_open()
        controller.mark_open("channel-1", "session-1")
        with self.assertRaises(ValueError):
            controller.accept_turn(
                TurnReceipt(
                    channel_id="channel-1",
                    session_id="session-1",
                    turn_index=1,
                    input_hash="in",
                    output_hash="out",
                    cumulative_root="root",
                    aggregate_gn=1,
                    miner_signature=b"miner",
                )
            )

    def test_delegation_policy_enforces_protocol_bounds(self) -> None:
        policy = DelegationPolicy(
            duration_blocks=100,
            per_tx_cap_flop=Decimal("10"),
            daily_cap_flop=Decimal("50"),
            allowed_pallets=frozenset({"compute_channel"}),
            allowed_destinations=frozenset({"miner-1"}),
        )
        policy.authorize(
            pallet="compute_channel",
            destination="miner-1",
            amount_flop=Decimal("5"),
            daily_spent_flop=Decimal("10"),
            window_tx_count=1,
            window_spent_flop=Decimal("10"),
        )
        with self.assertRaises(PolicyViolation):
            policy.authorize(
                pallet="compute_channel",
                destination="miner-1",
                amount_flop=Decimal("11"),
                daily_spent_flop=Decimal("10"),
                window_tx_count=1,
                window_spent_flop=Decimal("10"),
            )

    def test_network_adapter_fails_closed(self) -> None:
        adapter = UnconfiguredFlopNetworkAdapter()
        with self.assertRaises(NetworkNotConfigured):
            adapter.claim_faucet()

    def test_evidence_ledger_is_append_only_and_hashable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "activity.jsonl"
            ledger = EvidenceLedger(path)
            ledger.append("channel_opened", channel_id="channel-1", data={"escrow": "10"})
            first_hash = ledger.sha256()
            ledger.append("settled", channel_id="channel-1", data={"aggregate_gn": 42})
            records = list(ledger.records())
            self.assertEqual(len(records), 2)
            self.assertNotEqual(first_hash, ledger.sha256())


if __name__ == "__main__":
    unittest.main()
