#!/usr/bin/env python3
"""
CLI MVP Gouttes d'Eau

Commandes : genkeys | encode | decode | verify | simulate-loss

Exit codes :
  0 = OK
  1 = Erreur signature / cle
  2 = Donnees corrompues
  3 = Shards manquants
  4 = Autre erreur
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Imports locaux
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fragmentation import (
    K,
    M,
    N,
    fragmenter,
    reconstruire,
    simuler_perte,
    sha256,
)
from signature import (
    generate_keypair,
    save_keypair,
    load_private_key,
    load_public_key,
    sign_meta,
    verify_meta,
)

VERSION = "0.5.0-mvp"


def cmd_genkeys(args: argparse.Namespace) -> int:
    out = Path(args.output)
    priv, pub = generate_keypair()
    priv_path, pub_path = save_keypair(out, priv, pub)
    print(f"Private key : {priv_path} (gardez-la secrete, permissions 600 si possible)")
    print(f"Public key  : {pub_path}")
    return 0


def cmd_encode(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Fichier introuvable : {input_path}", file=sys.stderr)
        return 4

    out_dir = Path(args.output)
    try:
        private_key = load_private_key(args.key)
    except Exception as e:
        print(f"Erreur cle privee : {e}", file=sys.stderr)
        return 1

    meta = fragmenter(str(input_path), str(out_dir), k=K, m=M)

    # Signer le manifeste
    signature = sign_meta(meta, private_key)
    meta["signature"] = signature
    meta_path = out_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Manifeste signe -> {meta_path}")
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    drops = Path(args.input)
    meta_path = drops / "meta.json"
    if not meta_path.exists():
        print("meta.json introuvable", file=sys.stderr)
        return 4

    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    if args.pubkey:
        try:
            public_key = load_public_key(args.pubkey)
        except Exception as e:
            print(f"Erreur cle publique : {e}", file=sys.stderr)
            return 1
        sig = meta.get("signature")
        if not sig:
            print("Manifeste non signe", file=sys.stderr)
            return 1
        if not verify_meta(meta, sig, public_key):
            print("Signature du manifeste INVALIDE", file=sys.stderr)
            return 1
        print("Signature manifeste : OK")

    out = Path(args.output)
    # Si output est un repertoire, reconstituer un nom de fichier
    if out.suffix == "" or out.is_dir():
        out.mkdir(parents=True, exist_ok=True)
        out = out / "restored.bin"

    ok = reconstruire(str(drops), str(out))
    if not ok:
        # Distinguer shards manquants vs corruption si possible
        present = len(list(drops.glob("goutte_*.bin")))
        k = meta.get("k", K)
        if present < k:
            print(f"Insufficient shards: {present}/{k} required", file=sys.stderr)
            return 3
        return 2
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    drops = Path(args.drops)
    meta_path = drops / "meta.json"
    if not meta_path.exists():
        print("meta.json introuvable", file=sys.stderr)
        return 4

    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    if args.pubkey:
        try:
            public_key = load_public_key(args.pubkey)
        except Exception as e:
            print(f"Erreur cle publique : {e}", file=sys.stderr)
            return 1
        sig = meta.get("signature")
        if not sig or not verify_meta(meta, sig, public_key):
            print("Signature : INVALIDE", file=sys.stderr)
            return 1
        print("Signature : OK")

    errors = 0
    for g in meta.get("gouttes", []):
        path = drops / g["fichier"]
        if not path.exists():
            print(f"  MANQUANT {g['fichier']}")
            continue
        h = sha256(path.read_bytes())
        if h != g["hash"]:
            print(f"  CORROMPU {g['fichier']}")
            errors += 1
        else:
            print(f"  OK {g['fichier']}")

    if errors:
        print(f"{errors} goutte(s) corrompue(s)")
        return 2
    print("All hashes match")
    return 0


def cmd_simulate_loss(args: argparse.Namespace) -> int:
    simuler_perte(args.drops, args.missing)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gouttes d'Eau CLI MVP")
    parser.add_argument("--version", action="version", version=f"gouttes-eau {VERSION}")
    sub = parser.add_subparsers(dest="cmd")

    p_keys = sub.add_parser("genkeys", help="Generer une paire Ed25519")
    p_keys.add_argument("--output", default=".gouttes-keys")

    p_enc = sub.add_parser("encode", help="Fragmenter + signer")
    p_enc.add_argument("--input", required=True)
    p_enc.add_argument("--output", default="gouttes")
    p_enc.add_argument("--key", required=True, help="Chemin private.key")

    p_dec = sub.add_parser("decode", help="Reconstruire (+ verifier signature si --pubkey)")
    p_dec.add_argument("--input", required=True, help="Dossier des gouttes")
    p_dec.add_argument("--output", required=True)
    p_dec.add_argument("--pubkey", default=None)

    p_ver = sub.add_parser("verify", help="Verifier signature et hashes")
    p_ver.add_argument("--drops", required=True)
    p_ver.add_argument("--pubkey", default=None)

    p_loss = sub.add_parser("simulate-loss", help="Supprimer N gouttes aleatoires")
    p_loss.add_argument("--drops", required=True)
    p_loss.add_argument("--missing", type=int, default=3)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 4

    handlers = {
        "genkeys": cmd_genkeys,
        "encode": cmd_encode,
        "decode": cmd_decode,
        "verify": cmd_verify,
        "simulate-loss": cmd_simulate_loss,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
