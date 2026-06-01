#!/usr/bin/env python3
"""Mint a block on Planisphere's mirror chain.

The mirror chain is an attestation ledger. Each block seals one EIP-712
attestation (its payload) and commits, EVM-canonically, to the block before it:

    blockHash = keccak256( rlp([ parentHash, number, timestamp,
                                 sealer, payloadRoot, signature ]) )

`parentHash` chains the blocks; change any earlier block and every later
blockHash moves. The genesis block (number 0) has `parentHash = 0x00..00`.
`payloadRoot` is the EIP-712 digest of the sealed attestation (see
seal_eip712.py) — so the block commits to the document, the signer, Room 137
and the timestamp through that one root. As above, so below.

Usage:
    python3 tools/mint_block.py            # mint genesis (block 0) from seal.json
    python3 tools/mint_block.py <parent.json>   # mint the next block onto <parent>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import rlp
from eth_utils import keccak, to_bytes

PUBLIC = Path(__file__).resolve().parent.parent / "public"
CHAIN_NAME = "planisphere-mirror"
ZERO_HASH = "0x" + "00" * 32


def _b(hexstr: str) -> bytes:
    return to_bytes(hexstr=hexstr)


def _block_hash(parent_hash, number, timestamp, sealer, payload_root, signature) -> str:
    header = [
        _b(parent_hash),
        number,
        timestamp,
        _b(sealer),
        _b(payload_root),
        _b(signature),
    ]
    return "0x" + keccak(rlp.encode(header)).hex()


def main() -> None:
    seal = json.loads((PUBLIC / "seal.json").read_text())
    payload_root = seal["digest"]
    sealer = seal["signer_address"]
    signature = seal["signature"]
    timestamp = seal["message"]["timestamp"]

    if len(sys.argv) > 1:
        parent = json.loads(Path(sys.argv[1]).read_text())
        parent_hash = parent["blockHash"]
        number = parent["number"] + 1
        out_name = f"block-{number}.json"
    else:
        parent_hash = ZERO_HASH
        number = 0
        out_name = "genesis.json"

    block_hash = _block_hash(
        parent_hash, number, timestamp, sealer, payload_root, signature
    )

    block = {
        "chain": CHAIN_NAME,
        "chainId": 1,
        "number": number,
        "genesis": number == 0,
        "parentHash": parent_hash,
        "timestamp": timestamp,
        "sealer": sealer,
        "payloadRoot": payload_root,
        "signature": signature,
        "blockHash": block_hash,
        "payload": seal,
        "verify": (
            "blockHash == keccak256(rlp([parentHash, number, timestamp, sealer, "
            "payloadRoot, signature])); payloadRoot is the EIP-712 digest in "
            "payload — ecrecover(payload) == sealer"
        ),
    }
    (PUBLIC / out_name).write_text(json.dumps(block, indent=2) + "\n")

    # recompute as an independent check
    assert (
        _block_hash(parent_hash, number, timestamp, sealer, payload_root, signature)
        == block_hash
    )
    print("chain     ", CHAIN_NAME)
    print("number    ", number, "(genesis)" if number == 0 else "")
    print("parentHash", parent_hash)
    print("payloadRoot", payload_root)
    print("blockHash ", block_hash)
    print("wrote     ", PUBLIC / out_name)


if __name__ == "__main__":
    main()
