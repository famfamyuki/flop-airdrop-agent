# FLOP Airdrop Agent

Testnet-ready agent project for useful and verifiable FLOP inference participation.

## Identity

Public DID:

`did:key:z6Mkm8EGUMktFBFhcrpC3dsvsdqQfoKZTxCUTvbv9pJ1GDJn`

This project uses a persistent Ed25519 `did:key` identity for signed participation. Private signing material is stored separately and must never be committed.

## Protocol pin

The pre-testnet harness is pinned to **FLOP Yellow Paper v0.5.0 draft (updated 2026-09-05)**:
https://flop.finance/intro/yellowpaper/

The Yellow Paper is still an iterating implementation specification. Runtime/RPC/faucet values must be re-verified against official testnet releases before live use.

## Current status

- [x] Persistent Ed25519 DID created and recovery verified
- [x] Signed Technocore introduction published; local evidence saved
- [x] Spec-pinned protocol profile
- [x] Agent-side compute-channel session state machine
- [x] Verify-before-counter-sign receipt boundary
- [x] Append-only neutral activity/evidence ledger
- [x] Fail-closed network adapter placeholder
- [ ] Official FLOP Testnet RPC/runtime binding
- [ ] Faucet integration
- [ ] Real sr25519/SCALE transcript verification and receipt signing
- [ ] Live `open_channel` / `settle` integration
- [ ] Inference workload routing

## Design rule

Build stable boundaries now; do not guess unpublished network details. There is intentionally no airdrop scoring, faucet automation, or spend-maximization logic while genesis conversion and vesting remain unresolved.

The intended flow is:

`IDLE -> OPENING -> OPEN -> STREAMING -> SETTLEMENT_PENDING -> SETTLED | FAILED`

Network-specific code stays behind `FlopNetworkPort`, so official Testnet details can be added without rewriting the session core.

## Run tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Security

Private seeds, signing keys, `.env` files, wallet material, and other secrets must remain outside Git.
