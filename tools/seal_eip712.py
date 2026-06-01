#!/usr/bin/env python3
"""Press an EVM-canonical (EIP-712) seal over the dissertation.

The canonical language is the EVM's: a document is sealed by signing an
EIP-712 typed-structured-data digest

    digest = keccak256( 0x19 0x01 || domainSeparator || hashStruct(message) )

with a secp256k1 key, recoverable to an address via ecrecover. Unlike a bare
hash, the digest commits to *named fields* — so the signer, Room, timestamp,
document hash and seal hash are all bound into the one thing that gets signed.
What the website shows above is exactly what is sealed below.

Key origin:
  - PLANISPHERE_SECP256K1_PRIVKEY_HEX in env  -> operator-held (production)
  - else a deterministic dev key derived from the committed hashes (reproducible;
    anyone with the inputs recovers the same address) -> "derived-dev"
"""
from __future__ import annotations

import calendar
import hashlib
import json
import os
from pathlib import Path

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import keccak

PUBLIC = Path(__file__).resolve().parent.parent / "public"


def _file_keccak(p: Path) -> str:
    return "0x" + keccak(p.read_bytes()).hex()


def _file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> None:
    pdf = PUBLIC / "thesis.pdf"
    svg = PUBLIC / "seal.svg"

    doc_keccak = _file_keccak(pdf)
    seal_keccak = _file_keccak(svg)
    timestamp = calendar.timegm((2026, 6, 1, 0, 0, 0))  # 2026-06-01T00:00:00Z

    domain = {
        "name": "Planisphere",
        "version": "1",
        "chainId": 1,
        "salt": "0x" + keccak(b"shadow-mirror-thesis|Room 137").hex(),
    }
    types = {
        "Attestation": [
            {"name": "document", "type": "string"},
            {"name": "signer", "type": "string"},
            {"name": "room", "type": "string"},
            {"name": "pages", "type": "uint256"},
            {"name": "documentHash", "type": "bytes32"},
            {"name": "sealHash", "type": "bytes32"},
            {"name": "timestamp", "type": "uint256"},
        ],
    }
    message = {
        "document": "Shadow & Mirror: Treewidth as the Universal Meter of "
        "Computation, Physics, and Consciousness",
        "signer": "Logan Christopher Ross",
        "room": "137",
        "pages": 895,
        "documentHash": doc_keccak,
        "sealHash": seal_keccak,
        "timestamp": timestamp,
    }

    signable = encode_typed_data(domain, types, message)

    env_key = os.environ.get("PLANISPHERE_SECP256K1_PRIVKEY_HEX")
    if env_key:
        privkey = env_key if env_key.startswith("0x") else "0x" + env_key
        key_origin = "env"
    else:
        seed = f"planisphere-eip712|{doc_keccak}|{seal_keccak}".encode()
        privkey = "0x" + hashlib.sha256(seed).hexdigest()
        key_origin = "derived-dev"

    acct = Account.from_key(privkey)
    signed = acct.sign_message(signable)
    digest = "0x" + signed.message_hash.hex()
    signature = "0x" + signed.signature.hex()

    recovered = Account.recover_message(signable, signature=signed.signature)
    assert recovered == acct.address, "ecrecover mismatch"

    out = {
        "instrument": "EIP-712 typed structured data, secp256k1 signature "
        "(EVM-canonical, ecrecover-verifiable)",
        "as_above_so_below": "every field shown on the page is a committed field "
        "of the signed message; the digest moves if any of them change",
        "domain": domain,
        "types": types,
        "message": message,
        "digest": digest,
        "signature": signature,
        "signer_address": acct.address,
        "key_origin": key_origin,
        "file_sha256": {
            "thesis.pdf": _file_sha256(pdf),
            "seal.svg": _file_sha256(svg),
        },
        "verify": "eth_account.Account.recover_message("
        "encode_typed_data(domain, types, message), signature=signature) "
        "== signer_address",
    }
    (PUBLIC / "seal.json").write_text(json.dumps(out, indent=2) + "\n")
    print("digest        ", digest)
    print("signer_address", acct.address)
    print("key_origin    ", key_origin)
    print("wrote         ", PUBLIC / "seal.json")


if __name__ == "__main__":
    main()
