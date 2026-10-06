#!/usr/bin/env python3
"""Tests UX CLI : batches, nom original, list."""

from __future__ import annotations

import json
import sys
import tempfile
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gouttes_cli import (
    cmd_encode,
    cmd_decode,
    cmd_list,
    cmd_simulate_loss,
    safe_basename,
)
from signature import generate_keypair, save_keypair
from fragmentation import M


def test_safe_basename():
    assert safe_basename("ok.m4a") == "ok.m4a"
    assert safe_basename("../../etc/passwd") == "passwd"
    assert safe_basename("..") == "restored.bin"
    assert safe_basename(None) == "restored.bin"
    print("OK  test_safe_basename")


def test_encode_list_decode_restore_name():
    data = b"hello gouttes batch ux #25715\n" * 20
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src = tmp / "fichier.m4a"
        src.write_bytes(data)
        keys = tmp / "keys"
        priv, pub = generate_keypair()
        save_keypair(keys, priv, pub)
        drops = tmp / "drops"
        restored = tmp / "restored"

        rc = cmd_encode(
            Namespace(input=str(src), output=str(drops), key=str(keys / "private.key"))
        )
        assert rc == 0
        batches = [p for p in drops.iterdir() if p.is_dir() and (p / "meta.json").exists()]
        assert len(batches) == 1, batches
        meta = json.loads((batches[0] / "meta.json").read_text())
        assert meta["original_filename"] == "fichier.m4a"
        assert "batch_id" in meta
        assert "signature" in meta

        rc = cmd_list(Namespace(drops=str(drops)))
        assert rc == 0

        rc = cmd_simulate_loss(Namespace(drops=str(batches[0]), missing=M))
        assert rc == 0

        rc = cmd_decode(
            Namespace(
                input=str(batches[0]),
                output=str(restored),
                pubkey=str(keys / "public.key"),
            )
        )
        assert rc == 0
        out = restored / "fichier.m4a"
        assert out.exists(), list(restored.iterdir())
        assert out.read_bytes() == data
    print("OK  test_encode_list_decode_restore_name")


def test_two_encodes_two_batches():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        keys = tmp / "keys"
        priv, pub = generate_keypair()
        save_keypair(keys, priv, pub)
        drops = tmp / "drops"
        a = tmp / "a.txt"
        b = tmp / "b.txt"
        a.write_text("aaa")
        b.write_text("bbb")
        assert cmd_encode(Namespace(input=str(a), output=str(drops), key=str(keys / "private.key"))) == 0
        assert cmd_encode(Namespace(input=str(b), output=str(drops), key=str(keys / "private.key"))) == 0
        batches = [p for p in drops.iterdir() if p.is_dir() and (p / "meta.json").exists()]
        assert len(batches) == 2
        names = {
            json.loads((p / "meta.json").read_text())["original_filename"] for p in batches
        }
        assert names == {"a.txt", "b.txt"}
    print("OK  test_two_encodes_two_batches")


if __name__ == "__main__":
    try:
        test_safe_basename()
        test_encode_list_decode_restore_name()
        test_two_encodes_two_batches()
        print("TOUS LES TESTS batches SONT PASSES")
        sys.exit(0)
    except Exception as e:
        print(f"ECHEC : {e}")
        raise
