#!/usr/bin/env python3
"""
CLI MVP Gouttes d'Eau

Commandes : genkeys | encode | decode | verify | simulate-loss | list

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
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fragmentation import (
    K,
    M,
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

VERSION = "0.5.1-mvp"


def make_batch_id(original_hash: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{ts}_{original_hash[:8]}_{os.urandom(3).hex()}"


def safe_basename(name: str | None, fallback: str = "restored.bin") -> str:
    """Nom de fichier sans chemin (evite ../)."""
    if not name:
        return fallback
    base = Path(name).name
    if not base or base in {".", ".."}:
        return fallback
    return base


def iter_batch_dirs(root: Path) -> list[Path]:
    """Dossiers contenant un meta.json (racine legacy ou sous-dossiers batch)."""
    if not root.exists():
        return []
    found: list[Path] = []
    if (root / "meta.json").exists():
        found.append(root)
    if root.is_dir():
        for child in sorted(root.iterdir()):
            if child.is_dir() and (child / "meta.json").exists() and child not in found:
                found.append(child)
    return found


def resolve_decode_output(output: Path, meta: dict) -> Path:
    name = safe_basename(meta.get("original_filename"), "restored.bin")
    out_str = str(output)
    if output.exists() and output.is_dir():
        return output / name
    if out_str.endswith(("/", "\\")) or output.suffix == "":
        output.mkdir(parents=True, exist_ok=True)
        return output / name
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def cmd_genkeys(args: argparse.Namespace) -> int:
    out = Path(args.output)
    priv, pub = generate_keypair()
    priv_path, pub_path = save_keypair(out, priv, pub)
    print(f"Private key : {priv_path} (gardez-la secrete, permissions 600 si possible)")
    print(f"Public key  : {pub_path}")
    return 0


def cmd_encode(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    if not input_path.exists() or not input_path.is_file():
        print(f"Fichier introuvable : {input_path}", file=sys.stderr)
        return 4

    try:
        private_key = load_private_key(args.key)
    except Exception as e:
        print(f"Erreur cle privee : {e}", file=sys.stderr)
        return 1

    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    staging = root / f".staging_{os.urandom(4).hex()}"
    staging.mkdir(parents=True, exist_ok=True)

    try:
        meta = fragmenter(str(input_path), str(staging), k=K, m=M)
        batch_id = make_batch_id(meta["original_hash"])
        meta["version"] = VERSION
        meta["batch_id"] = batch_id
        meta["timestamp"] = datetime.now(timezone.utc).isoformat()
        meta["original_filename"] = safe_basename(input_path.name)
        signature = sign_meta(meta, private_key)
        meta["signature"] = signature
        (staging / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        dest = root / batch_id
        if dest.exists():
            dest = root / f"{batch_id}_{os.urandom(2).hex()}"
        staging.rename(dest)
    except Exception:
        # nettoyage staging si echec
        try:
            for p in staging.glob("*"):
                p.unlink()
            staging.rmdir()
        except OSError:
            pass
        raise

    print(f"Batch ID : {meta['batch_id']}")
    print(f"Fichier original : {meta['original_filename']}")
    print(f"Manifeste signe -> {dest / 'meta.json'}")
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
        if meta.get("batch_id"):
            print(f"Batch : {meta['batch_id']}")
        if meta.get("original_filename"):
            print(f"Fichier attendu : {meta['original_filename']}")

    out = resolve_decode_output(Path(args.output), meta)
    ok = reconstruire(str(drops), str(out))
    if not ok:
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


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.drops)
    batches = iter_batch_dirs(root)
    if not batches:
        print(f"Aucun batch trouve dans {root}")
        return 0

    print(f"BATCHES ({len(batches)}) dans {root}")
    rows = []
    for d in batches:
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        n = meta.get("n", 10)
        present = sum(1 for i in range(n) if (d / f"goutte_{i:02d}.bin").exists())
        rows.append(
            {
                "dir": str(d),
                "batch_id": meta.get("batch_id", d.name),
                "filename": meta.get("original_filename", "?"),
                "size": meta.get("original_size", 0),
                "present": present,
                "n": n,
                "k": meta.get("k", "?"),
                "created": meta.get("timestamp", "?"),
            }
        )
    rows.sort(key=lambda r: str(r["created"]), reverse=True)
    for b in rows:
        print(f"\n[ {b['batch_id']} ]")
        print(f"  Dossier : {b['dir']}")
        print(f"  Fichier : {b['filename']}")
        print(f"  Taille  : {b['size']} octets")
        print(f"  Shards  : {b['present']}/{b['n']} (K={b['k']})")
        print(f"  Cree    : {b['created']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gouttes d'Eau CLI MVP")
    parser.add_argument("--version", action="version", version=f"gouttes-eau {VERSION}")
    sub = parser.add_subparsers(dest="cmd")

    p_keys = sub.add_parser("genkeys", help="Generer une paire Ed25519")
    p_keys.add_argument("--output", default=".gouttes-keys")

    p_enc = sub.add_parser("encode", help="Fragmenter + signer (sous-dossier batch)")
    p_enc.add_argument("--input", required=True)
    p_enc.add_argument("--output", default="gouttes")
    p_enc.add_argument("--key", required=True, help="Chemin private.key (binaire 32 octets)")

    p_dec = sub.add_parser("decode", help="Reconstruire (+ verifier signature si --pubkey)")
    p_dec.add_argument("--input", required=True, help="Dossier d'un batch (celui qui contient meta.json)")
    p_dec.add_argument("--output", required=True, help="Dossier ou fichier de sortie")
    p_dec.add_argument("--pubkey", default=None)

    p_ver = sub.add_parser("verify", help="Verifier signature et hashes")
    p_ver.add_argument("--drops", required=True)
    p_ver.add_argument("--pubkey", default=None)

    p_loss = sub.add_parser("simulate-loss", help="Supprimer N gouttes aleatoires")
    p_loss.add_argument("--drops", required=True, help="Dossier d'un batch")
    p_loss.add_argument("--missing", type=int, default=3)

    p_list = sub.add_parser("list", help="Lister les batches")
    p_list.add_argument("--drops", required=True, help="Racine contenant des sous-dossiers batch")

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
        "list": cmd_list,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
