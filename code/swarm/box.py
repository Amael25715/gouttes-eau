"""Chiffre le fichier, puis fragmente le chiffré. Une goutte seule ne suffit pas, dix non plus sans la clé."""

from __future__ import annotations

import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from swarm.rs import K, M, N, decode_shards, encode_shards, sha256

FILE_AAD = b"gouttes-file-v1"
TICKET_AAD = b"gouttes-ticket-v1"


def new_key() -> bytes:
    return os.urandom(32)


def seal(key: bytes, plaintext: bytes, aad: bytes) -> bytes:
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, plaintext, aad)


def open_sealed(key: bytes, blob: bytes, aad: bytes) -> bytes:
    if len(blob) < 12 + 16:
        raise ValueError("blob chiffré trop court")
    nonce, ct = blob[:12], blob[12:]
    return AESGCM(key).decrypt(nonce, ct, aad)


def build_ticket(filename: str, plaintext: bytes, key: bytes) -> tuple[dict, list[tuple[str, bytes]], bytes]:
    """Retourne (ticket clair, [(drop_id, shard)], ticket_blob).

    Le ticket clair ne contient aucun hôte. Le blob est ce qu'on disperse.
    """
    cipher = seal(key, plaintext, FILE_AAD)
    shards = encode_shards(cipher)
    drops = [(sha256(shard), shard) for shard in shards]
    ticket = {
        "v": 1,
        "filename": filename,
        "plain_size": len(plaintext),
        "plain_hash": sha256(plaintext),
        "cipher_size": len(cipher),
        "k": K,
        "m": M,
        "n": N,
        "drop_ids": [drop_id for drop_id, _ in drops],
    }
    blob = seal(key, json.dumps(ticket, separators=(",", ":")).encode("utf-8"), TICKET_AAD)
    return ticket, drops, blob


def open_ticket(key: bytes, blob: bytes) -> dict:
    return json.loads(open_sealed(key, blob, TICKET_AAD))


def rebuild(key: bytes, ticket: dict, shards: list[bytes | None]) -> bytes:
    cipher = decode_shards(shards, ticket["cipher_size"], k=ticket["k"], m=ticket["m"])
    # seal() a préfixé le nonce : le chiffré RS est nonce||ct||tag, open_sealed le gère.
    plain = open_sealed(key, cipher, FILE_AAD)
    if sha256(plain) != ticket["plain_hash"]:
        raise ValueError("hash clair incorrect")
    return plain
