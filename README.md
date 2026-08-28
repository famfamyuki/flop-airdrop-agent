# FLOP Airdrop Agent

Testnet-ready agent project for useful and verifiable FLOP inference participation.

## Identity

Public DID:

did:key:z6Mkm8EGUMktFBFhcrpC3dsvsdqQfoKZTxCUTvbv9pJ1GDJn

This project uses a persistent Ed25519 did:key identity for signed participation.

## Current status

- [x] Persistent Ed25519 DID created
- [x] Private seed stored separately
- [x] DID recovery verified
- [x] Signed Technocore introduction published
- [x] Local evidence saved
- [ ] FLOP Testnet adapter
- [ ] Faucet integration
- [ ] Inference workload integration
- [ ] Activity and spend ledger
- [ ] Evidence export

## Security

Private signing material is never committed to this repository.

The Ed25519 seed, private keys, .env files, and other secrets must remain outside Git.
