#!/usr/bin/env python3
"""
Tests automatiques du POC Gouttes d'eau.
À lancer : python code/test_gouttes.py
Ou via GitHub Actions à chaque push.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

# Permettre l'import depuis le même dossier
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fragmentation import K, M, N, fragmenter, reconstruire, simuler_perte, _encode_shards, _decode_shards, sha256


def assert_true(cond: bool, msg: str):
    if not cond:
        raise AssertionError(msg)


def test_roundtrip_no_loss():
    data = b"Alignement #25715 #3581215 - test sans perte\n" * 50
    shards, size = _encode_shards(data)
    assert_true(len(shards) == N, f"Attendu {N} shards")
    recovered = _decode_shards(list(shards), size)
    assert_true(recovered == data, "Roundtrip sans perte échoué")
    print("OK  test_roundtrip_no_loss")


def test_recovery_after_m_losses():
    data = b"Preuve résilience gouttes - on perd M shards\n" * 40
    shards, size = _encode_shards(data)
    # Perdre exactement M shards
    lost = list(range(M))  # 0..M-1
    partial = [None if i in lost else s for i, s in enumerate(shards)]
    recovered = _decode_shards(partial, size)
    assert_true(recovered == data, "Reconstruction après perte de M shards échouée")
    print(f"OK  test_recovery_after_m_losses (perdu {lost})")


def test_fail_if_too_many_losses():
    data = b"Doit echouer si trop de pertes\n" * 20
    shards, size = _encode_shards(data)
    # Perdre M+1 shards
    lost = list(range(M + 1))
    partial = [None if i in lost else s for i, s in enumerate(shards)]
    try:
        _decode_shards(partial, size)
        raise AssertionError("Aurait dû échouer avec M+1 pertes")
    except ValueError:
        print(f"OK  test_fail_if_too_many_losses (perdu {lost})")


def test_filesystem_workflow():
    data = (
        b"Message d'alignement #25715 pour preuve locale des gouttes d'eau.\n"
        b"Cycles fermes, anti-pyramide, interdependance.\n"
    ) * 30

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        original = tmp_path / "original.bin"
        original.write_bytes(data)
        gouttes = tmp_path / "gouttes"
        out = tmp_path / "reconstruit.bin"

        fragmenter(str(original), str(gouttes))
        assert_true((gouttes / "meta.json").exists(), "meta.json manquant")
        assert_true(len(list(gouttes.glob("goutte_*.bin"))) == N, f"Attendu {N} fichiers goutte")

        # Perdre M gouttes
        simuler_perte(str(gouttes), nombre_a_supprimer=M)
        remaining = list(gouttes.glob("goutte_*.bin"))
        assert_true(len(remaining) == N - M, f"Attendu {N - M} gouttes restantes")

        ok = reconstruire(str(gouttes), str(out))
        assert_true(ok, "reconstruire a renvoyé False")
        assert_true(out.read_bytes() == data, "Contenu reconstruit différent de l'original")
        assert_true(sha256(out.read_bytes()) == sha256(data), "Hash différent")

    print("OK  test_filesystem_workflow (fragmenter → perdre M → reconstruire)")


def main():
    print(f"Paramètres : K={K} M={M} N={N}")
    print("---")
    test_roundtrip_no_loss()
    test_recovery_after_m_losses()
    test_fail_if_too_many_losses()
    test_filesystem_workflow()
    print("---")
    print("TOUS LES TESTS SONT PASSES")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ECHEC : {e}")
        sys.exit(1)
