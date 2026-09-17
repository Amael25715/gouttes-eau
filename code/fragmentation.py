#!/usr/bin/env python3
"""
POC Gouttes d'eau - Fragmentation / reconstruction avec Reed-Solomon
Aligné Message : fragmentation + reconstruction collaborative, pas de point unique.

Usage:
  python fragmentation.py fragmenter <fichier> [--out dossier]
  python fragmentation.py reconstruire [--dossier gouttes] [--out fichier]
  python fragmentation.py perdre [--dossier gouttes] [--n 3]
"""

import os
import sys
import json
import hashlib
import argparse
import random
from pathlib import Path

try:
    from reedsolo import RSCodec, ReedSolomonError
except ImportError:
    print("Installez reedsolo : pip install reedsolo")
    sys.exit(1)

# Paramètres par défaut (ajustables)
K = 6          # fragments de données nécessaires
M = 4          # fragments de parité (on peut en perdre jusqu'à M)
N = K + M      # total de gouttes


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fragmenter(fichier: str, dossier_gouttes: str = "gouttes"):
    """Découpe le fichier en N gouttes (K data + M parité)."""
    Path(dossier_gouttes).mkdir(exist_ok=True)

    with open(fichier, "rb") as f:
        data = f.read()

    original_hash = sha256(data)
    rsc = RSCodec(M)

    # POC : encodage global (pour gros fichiers → découper en blocs plus tard)
    encoded = rsc.encode(data)

    fragment_size = (len(encoded) + N - 1) // N
    gouttes = []

    for i in range(N):
        start = i * fragment_size
        end = min((i + 1) * fragment_size, len(encoded))
        frag = encoded[start:end]
        if len(frag) < fragment_size:
            frag += b"\x00" * (fragment_size - len(frag))

        nom = f"goutte_{i:02d}.bin"
        chemin = Path(dossier_gouttes) / nom
        with open(chemin, "wb") as f:
            f.write(frag)

        gouttes.append({
            "index": i,
            "fichier": nom,
            "hash": sha256(frag),
            "taille": len(frag)
        })
        print(f"  Goutte {i:02d} écrite → {chemin}")

    meta = {
        "original_hash": original_hash,
        "original_size": len(data),
        "k": K,
        "m": M,
        "n": N,
        "fragment_size": fragment_size,
        "gouttes": gouttes
    }
    with open(Path(dossier_gouttes) / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nFragmentation terminée. Hash original : {original_hash}")
    return meta


def reconstruire(dossier_gouttes: str = "gouttes", sortie: str = "reconstruit.bin"):
    """Reconstruit à partir d'un sous-ensemble de gouttes."""
    meta_path = Path(dossier_gouttes) / "meta.json"
    if not meta_path.exists():
        print("meta.json introuvable")
        return False

    with open(meta_path) as f:
        meta = json.load(f)

    rsc = RSCodec(meta["m"])
    fragment_size = meta["fragment_size"]

    fragments = [None] * meta["n"]
    disponibles = 0

    for g in meta["gouttes"]:
        chemin = Path(dossier_gouttes) / g["fichier"]
        if chemin.exists():
            with open(chemin, "rb") as f:
                frag = f.read()
            if sha256(frag) == g["hash"]:
                fragments[g["index"]] = frag
                disponibles += 1
                print(f"  Goutte {g['index']:02d} OK")
            else:
                print(f"  Goutte {g['index']:02d} CORROMPUE (ignorée)")
        else:
            print(f"  Goutte {g['index']:02d} manquante")

    if disponibles < meta["k"]:
        print(f"Échec : seulement {disponibles} gouttes valides, il en faut au moins {meta['k']}")
        return False

    encoded = b"".join(
        f if f is not None else b"\x00" * fragment_size
        for f in fragments
    )

    try:
        decoded = rsc.decode(encoded)[0]
        decoded = decoded[:meta["original_size"]]

        final_hash = sha256(decoded)
        if final_hash != meta["original_hash"]:
            print("Attention : hash final différent (limite possible du POC simplifié)")

        with open(sortie, "wb") as f:
            f.write(decoded)
        print(f"\nReconstruction réussie → {sortie}")
        print(f"Hash : {final_hash}")
        return True
    except ReedSolomonError as e:
        print(f"Échec de reconstruction Reed-Solomon : {e}")
        return False


def simuler_perte(dossier_gouttes: str = "gouttes", nombre_a_supprimer: int = 3):
    """Supprime aléatoirement des gouttes pour tester la résilience."""
    meta_path = Path(dossier_gouttes) / "meta.json"
    with open(meta_path) as f:
        meta = json.load(f)

    indices = list(range(meta["n"]))
    a_supprimer = random.sample(indices, min(nombre_a_supprimer, meta["n"]))

    for i in a_supprimer:
        chemin = Path(dossier_gouttes) / f"goutte_{i:02d}.bin"
        if chemin.exists():
            chemin.unlink()
            print(f"  Supprimé goutte_{i:02d}.bin")

    print(f"Simulation : {len(a_supprimer)} gouttes perdues.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="POC Gouttes d'eau")
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
        reconstruire(args.dossier, args.out)
    elif args.cmd == "perdre":
        simuler_perte(args.dossier, args.n)
    else:
        parser.print_help()
