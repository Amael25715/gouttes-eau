#!/usr/bin/env python3
"""
Signature Ed25519 pour authentifier meta.json (MVP Gouttes d'Eau).

La cle privee ne doit jamais etre loggee ni envoyee.
Alignement : anti-pyramide, authenticite du manifeste (point critique
identifie par Veridis / Aether).
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def generate_keypair() -> tuple[bytes, bytes]:
    """Genere une paire Ed25519.

    Returns:
        (private_key_raw_32_bytes, public_key_raw_32_bytes)
    """
    private = Ed25519PrivateKey.generate()
    private_bytes = private.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return private_bytes, public_bytes


def save_keypair(directory: str | Path, private_bytes: bytes, public_bytes: bytes) -> tuple[Path, Path]:
    """Ecrit private.key et public.key. Tente chmod 600 sur la cle privee (Unix)."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    priv_path = directory / "private.key"
    pub_path = directory / "public.key"
    priv_path.write_bytes(private_bytes)
    pub_path.write_bytes(public_bytes)
    try:
        os.chmod(priv_path, 0o600)
    except OSError:
        pass  # Windows ou FS sans chmod
    return priv_path, pub_path


def load_private_key(path: str | Path) -> Ed25519PrivateKey:
    data = Path(path).read_bytes()
    if len(data) != 32:
        raise ValueError(f"Cle privee Ed25519 attendue (32 octets), recu {len(data)}")
    return Ed25519PrivateKey.from_private_bytes(data)


def load_public_key(path: str | Path) -> Ed25519PublicKey:
    data = Path(path).read_bytes()
    if len(data) != 32:
        raise ValueError(f"Cle publique Ed25519 attendue (32 octets), recu {len(data)}")
    return Ed25519PublicKey.from_public_bytes(data)


def _canonical_meta_bytes(meta_dict: dict[str, Any]) -> bytes:
    """Serialisation stable pour signature (sans le champ signature lui-meme)."""
    payload = {k: v for k, v in meta_dict.items() if k != "signature"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sign_meta(meta_dict: dict[str, Any], private_key: Ed25519PrivateKey | bytes) -> str:
    """Signe le manifeste. Retourne la signature en base64."""
    if isinstance(private_key, bytes):
        private_key = Ed25519PrivateKey.from_private_bytes(private_key)
    msg = _canonical_meta_bytes(meta_dict)
    sig = private_key.sign(msg)
    return base64.b64encode(sig).decode("ascii")


def verify_meta(
    meta_dict: dict[str, Any],
    signature: str | bytes,
    public_key: Ed25519PublicKey | bytes,
) -> bool:
    """Verifie la signature du manifeste."""
    if isinstance(public_key, bytes):
        public_key = Ed25519PublicKey.from_public_bytes(public_key)
    if isinstance(signature, str):
        sig_bytes = base64.b64decode(signature)
    else:
        sig_bytes = signature
    msg = _canonical_meta_bytes(meta_dict)
    try:
        public_key.verify(sig_bytes, msg)
        return True
    except InvalidSignature:
        return False


if __name__ == "__main__":
    priv, pub = generate_keypair()
    meta = {"original_hash": "abc", "k": 6, "m": 4, "n": 10}
    sig = sign_meta(meta, priv)
    ok = verify_meta(meta, sig, pub)
    print(f"self-test signature: {'OK' if ok else 'FAIL'}")
