"""Reed-Solomon K=6 M=4. Même construction que code/fragmentation.py (déjà testée)."""

from __future__ import annotations

import hashlib

from reedsolo import RSCodec

K = 6
M = 4
N = K + M


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_shards(data: bytes, k: int = K, m: int = M) -> list[bytes]:
    n = k + m
    pad = (k - (len(data) % k)) % k
    padded = data + b"\x00" * pad
    shard_len = len(padded) // k
    data_shards = [bytearray(padded[i * shard_len : (i + 1) * shard_len]) for i in range(k)]
    parity_shards = [bytearray(shard_len) for _ in range(m)]
    rsc = RSCodec(m, nsize=n)
    for pos in range(shard_len):
        row = bytes(data_shards[i][pos] for i in range(k))
        encoded = rsc.encode(row)
        for j in range(m):
            parity_shards[j][pos] = encoded[k + j]
    return [bytes(s) for s in data_shards] + [bytes(s) for s in parity_shards]


def decode_shards(shards: list[bytes | None], original_size: int, k: int = K, m: int = M) -> bytes:
    n = k + m
    if len(shards) != n:
        raise ValueError(f"attendu {n} slots, reçu {len(shards)}")
    present = [s for s in shards if s is not None]
    if len(present) < k:
        raise ValueError(f"{len(present)} shards, il en faut {k}")
    shard_len = len(present[0])
    lost = [i for i in range(n) if shards[i] is None]
    rsc = RSCodec(m, nsize=n)
    recovered = bytearray(k * shard_len)
    for pos in range(shard_len):
        received = bytearray(n)
        erase_pos = []
        for i in range(n):
            if i in lost:
                received[i] = 0
                erase_pos.append(i)
            else:
                received[i] = shards[i][pos]
        decoded = rsc.decode(bytes(received), erase_pos=erase_pos)[0]
        for i in range(k):
            recovered[i * shard_len + pos] = decoded[i]
    return bytes(recovered[:original_size])
