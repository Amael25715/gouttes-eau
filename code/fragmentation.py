#!/usr/bin/env python3
"""
POC Gouttes d'eau - Fragmentation / reconstruction par shards Reed-Solomon
Aligné Message : fragmentation + reconstruction collaborative, pas de point unique.

Principe correct :
- On découpe les données en K shards de données
- On calcule M shards de parité (stripe par stripe)
- Toute combinaison de K shards parmi N = K+M permet de reconstruire

Usage:
  python fragmentation.py fragmenter <fichier> [--out dossier]
  python fragmentation.py reconstruire [--dossier gouttes] [--out fichier]
  python fragmentation.py perdre [--dossier gouttes] [--n 3]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

try:
    from reedsolo import RSCodec, ReedSolomonError
except ImportError:
    print("Installez reedsolo : pip install reedsolo")
    sys.exit(1)

# Paramètres par défaut
K = 6  # shards de données nécessaires
M = 4  # shards de parité (on peut en perdre jusqu'à M)
N = K + M


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _encode_shards(data: bytes, k: int = K, m: int = M) -> tuple[list[bytes], int]:
    """Encode data en k + m shards. Retourne (liste de shards, taille originale)."""
    n = k + m
    pad = (k - len(data) % k) % k
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

    shards = [bytes(s) for s in data_shards] + [bytes(s) for s in parity_shards]
    return shards, len(data)


def _decode_shards(
    shards: list[bytes | None],
    original_size: int,
    k: int = K,
    m: int = M,
) -> bytes:
    """Reconstruit les données à partir d'une liste de shards (None = manquant)."""
    n = k + m
    if len(shards) != n:
        raise ValueError(f"Attendu {n} slots de shards, reçu {len(shards)}")

    present = [i for i, s in enumerate(shards) if s is not None]
    if len(present) < k:
        raise ValueError(f"Seulement {len(present)} shards, il en faut au moins {k}")

    shard_len = len(next(s for s in shards if s is not None))
    for s in shards:
        if s is not None and len(s) != shard_len:
            raise ValueError("Shards de tailles incohérentes")

    lost = [i for i in range(n) if shards[i] is None]
    rsc = RSCodec(m, nsize=n)
    recovered_padded = bytearray(k * shard_len)

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
            recovered_padded[i * shard_len + pos] = decoded[i]

    return bytes(recovered_padded[:original_size])


def fragmenter(fichier: str, dossier_gouttes: str = "gouttes", k: int = K, m: int = M):
    """Découpe le fichier en N = k+m gouttes."""
    path = Path(fichier)
    if not path.exists():
        raise FileNotFoundError(fichier)

    data = path.read_bytes()
    original_hash = sha256(data)
    shards, original_size = _encode_shards(data, k=k, m=m)
    n = k + m

    out = Path(dossier_gouttes)
    out.mkdir(parents=True, exist_ok=True)

    gouttes_meta = []
    for i, shard in enumerate(shards):
        nom = f"goutte_{i:02d}.bin"
        (out / nom).write_bytes(shard)
        gouttes_meta.append({"index": i, "fichier": nom, "hash": sha256(shard), "taille": len(shard)})
        print(f"  Goutte {i:02d} écrite → {out / nom} ({len(shard)} octets)")

    meta = {
        "original_hash": original_hash,
        "original_size": original_size,
        "k": k,
        "m": m,
        "n": n,
        "shard_size": len(shards[0]),
        "gouttes": gouttes_meta,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"\nFragmentation terminée. Hash original : {original_hash}")
    print(f"Paramètres : K={k} M={m} N={n} — on peut perdre jusqu'à {m} gouttes.")
    return meta


def reconstruire(dossier_gouttes: str = "gouttes", sortie: str = "reconstruit.bin") -> bool:
    """Reconstruit à partir des gouttes disponibles."""
    dossier = Path(dossier_gouttes)
    meta_path = dossier / "meta.json"
    if not meta_path.exists():
        print("meta.json introuvable")
        return False

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    k, m, n = meta["k"], meta["m"], meta["n"]

    shards: list[bytes | None] = [None] * n
    disponibles = 0

    for g in meta["gouttes"]:
        chemin = dossier / g["fichier"]
        idx = g["index"]
        if chemin.exists():
            frag = chemin.read_bytes()
            if sha256(frag) == g["hash"]:
                shards[idx] = frag
                disponibles += 1
                print(f"  Goutte {idx:02d} OK")
            else:
                print(f"  Goutte {idx:02d} CORROMPUE (ignorée)")
        else:
            print(f"  Goutte {idx:02d} manquante")

    if disponibles < k:
        print(f"Échec : seulement {disponibles} gouttes valides, il en faut au moins {k}")
        return False

    try:
        decoded = _decode_shards(shards, meta["original_size"], k=k, m=m)
    except (ReedSolomonError, ValueError) as e:
        print(f"Échec de reconstruction : {e}")
        return False

    final_hash = sha256(decoded)
    Path(sortie).write_bytes(decoded)

    if final_hash != meta["original_hash"]:
        print(f"ERREUR : hash final différent\n  attendu : {meta['original_hash']}\n  obtenu  : {final_hash}")
        return False

    print(f"\nReconstruction réussie → {sortie}")
    print(f"Hash : {final_hash}")
    return True


def simuler_perte(dossier_gouttes: str = "gouttes", nombre_a_supprimer: int = 3):
    """Supprime aléatoirement des gouttes pour tester la résilience."""
    dossier = Path(dossier_gouttes)
    meta = json.loads((dossier / "meta.json").read_text(encoding="utf-8"))
    indices = list(range(meta["n"]))
    a_supprimer = random.sample(indices, min(nombre_a_supprimer, meta["n"]))

    for i in a_supprimer:
        chemin = dossier / f"goutte_{i:02d}.bin"
        if chemin.exists():
            chemin.unlink()
            print(f"  Supprimé goutte_{i:02d}.bin")

    print(f"Simulation : {len(a_supprimer)} gouttes perdues.")
    return a_supprimer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="POC Gouttes d'eau (Reed-Solomon shards)")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("fragmenter", help="Fragmenter un fichier")
    p1.add_argument("fichier")
    p1.add_argument("--out", default="gouttes")

    p2 = sub.add_parser("reconstruire", help="Reconstruire")
    p2.add_argument("--dossier", default="gouttes")
    p2.add_argument("--out", default="reconstruit.bin")

    p3 = sub.add_parser("perdre", help="Simuler la perte de gouttes")
    p3.add_argument("--dossier", default="gouttes")
    p3.add_argument("--n", type=int, default=3)

    args = parser.parse_args()

    if args.cmd == "fragmenter":
        fragmenter(args.fichier, args.out)
    elif args.cmd == "reconstruire":
        ok = reconstruire(args.dossier, args.out)
        sys.exit(0 if ok else 1)
    elif args.cmd == "perdre":
        simuler_perte(args.dossier, args.n)
    else:
        parser.print_help()
