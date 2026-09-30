#!/usr/bin/env python3
"""Tests signature Ed25519 + workflow CLI encode/decode signe."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from signature import (
    generate_keypair,
    sign_meta,
    verify_meta,
    save_keypair,
    load_private_key,
    load_public_key,
)
from fragmentation import fragmenter, reconstruire, simuler_perte, M, N


def test_sign_verify_ok():
    priv, pub = generate_keypair()
    meta = {"original_hash": "deadbeef", "k": 6, "m": 4, "n": 10}
    sig = sign_meta(meta, priv)
    assert verify_meta(meta, sig, pub)
    print("OK  test_sign_verify_ok")


def test_sign_verify_tamper():
    priv, pub = generate_keypair()
    meta = {"original_hash": "deadbeef", "k": 6}
    sig = sign_meta(meta, priv)
    meta["original_hash"] = "tampered"
    assert not verify_meta(meta, sig, pub)
    print("OK  test_sign_verify_tamper")


def test_save_load_keys():
    with tempfile.TemporaryDirectory() as tmp:
        priv, pub = generate_keypair()
        save_keypair(tmp, priv, pub)
        p = load_private_key(Path(tmp) / "private.key")
        u = load_public_key(Path(tmp) / "public.key")
        meta = {"x": 1}
        sig = sign_meta(meta, p)
        assert verify_meta(meta, sig, u)
    print("OK  test_save_load_keys")


def test_encode_sign_loss_decode():
    """Workflow complet : fragmenter, signer, perdre M gouttes, verifier, reconstruire."""
    data = b"MVP signed workflow #25715\n" * 40
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        original = tmp / "orig.bin"
        original.write_bytes(data)
        drops = tmp / "drops"
        priv, pub = generate_keypair()
        keydir = tmp / "keys"
        save_keypair(keydir, priv, pub)

        meta = fragmenter(str(original), str(drops))
        sig = sign_meta(meta, priv)
        meta["signature"] = sig
        (drops / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        assert verify_meta(meta, sig, pub)

        simuler_perte(str(drops), M)
        out = tmp / "out.bin"
        ok = reconstruire(str(drops), str(out))
        assert ok, "reconstruction echouee apres perte M"
        assert out.read_bytes() == data
    print("OK  test_encode_sign_loss_decode")


if __name__ == "__main__":
    try:
        test_sign_verify_ok()
        test_sign_verify_tamper()
        test_save_load_keys()
        test_encode_sign_loss_decode()
        print("TOUS LES TESTS signature SONT PASSES")
        sys.exit(0)
    except Exception as e:
        print(f"ECHEC : {e}")
        sys.exit(1)
