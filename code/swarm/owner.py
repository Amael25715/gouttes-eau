"""Le propriétaire ne conserve que : la clé, le ticket_id, UNE adresse d'introduction.

Pas d'adresse de goutte. Pas de liste du réseau dans le reçu.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from swarm.box import build_ticket, new_key, open_ticket, rebuild
from swarm.protocol import rpc
from swarm.rs import M, sha256


def hello_peers(introducer: tuple[str, int]) -> list[dict]:
    header, _ = rpc(
        introducer[0],
        introducer[1],
        {"op": "HELLO", "role": "client"},
        timeout=3,
    )
    if header.get("op") != "PEERS":
        raise RuntimeError(f"HELLO refusé : {header}")
    return header["peers"]


def put_blob(peer: dict, drop_id: str, body: bytes) -> None:
    header, _ = rpc(peer["host"], int(peer["port"]), {"op": "PUT", "drop_id": drop_id}, body, timeout=10)
    if header.get("op") != "OK":
        raise RuntimeError(f"PUT {drop_id[:8]} vers {peer['id']} : {header}")


def find_blob(introducer: tuple[str, int], drop_id: str) -> bytes:
    header, body = rpc(introducer[0], introducer[1], {"op": "FIND", "drop_id": drop_id}, timeout=20)
    if header.get("op") != "DATA" or sha256(body) != drop_id:
        raise RuntimeError(f"FIND {drop_id[:8]} introuvable via {introducer[0]}:{introducer[1]}")
    return body


def cmd_put(args: argparse.Namespace) -> int:
    key_path = Path(args.key)
    if key_path.exists():
        key = key_path.read_bytes()
        if len(key) != 32:
            print("clé : 32 octets attendus", file=sys.stderr)
            return 1
    else:
        key = new_key()
        key_path.write_bytes(key)
        try:
            key_path.chmod(0o600)
        except OSError:
            pass
        print(f"clé créée : {key_path}")

    plain = Path(args.file).read_bytes()
    _ticket, drops, ticket_blob = build_ticket(Path(args.file).name, plain, key)
    ticket_id = sha256(ticket_blob)
    intro = _parse_addr(args.introducer)
    peers = hello_peers(intro)
    if not peers:
        print("aucun pair", file=sys.stderr)
        return 4

    for index, (drop_id, shard) in enumerate(drops):
        peer = peers[index % len(peers)]
        put_blob(peer, drop_id, shard)
        print(f"  goutte {index:02d} déposée ({drop_id[:12]})")

    worst = max(sum(1 for i in range(len(drops)) if i % len(peers) == slot) for slot in range(len(peers)))
    print(f"répartition : {len(peers)} hôte(s), le plus chargé en a {worst} (tolérance {M})")
    if worst > M:
        print(f"ATTENTION : si cet hôte disparaît, la relecture échoue. Il en faut assez pour qu'aucun n'en ait plus de {M}.")

    for peer in peers:
        put_blob(peer, ticket_id, ticket_blob)
    print(f"ticket {ticket_id[:12]} répliqué sur {len(peers)} pair(s)")

    receipt = {"v": 1, "ticket_id": ticket_id, "filename": Path(args.file).name}
    Path(args.receipt).write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"reçu : {args.receipt}")
    print("Ce reçu n'a pas d'adresse. Pour relire : la clé + ticket_id + un introducteur vivant.")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    key = Path(args.key).read_bytes()
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    ticket_id = args.ticket_id or receipt["ticket_id"]
    intro = _parse_addr(args.introducer)
    ticket_blob = find_blob(intro, ticket_id)
    ticket = open_ticket(key, ticket_blob)
    shards: list[bytes | None] = []
    missing = 0
    for drop_id in ticket["drop_ids"]:
        try:
            shards.append(find_blob(intro, drop_id))
        except RuntimeError:
            shards.append(None)
            missing += 1
    print(f"gouttes manquantes : {missing} (tolérance {ticket['m']})")
    if missing > ticket["m"]:
        print("trop de pertes", file=sys.stderr)
        return 3
    plain = rebuild(key, ticket, shards)
    out = Path(args.output)
    if out.is_dir() or str(args.output).endswith("/"):
        out.mkdir(parents=True, exist_ok=True)
        out = out / ticket["filename"]
    out.write_bytes(plain)
    print(f"OK {out} ({len(plain)} octets)")
    return 0


def _parse_addr(text: str) -> tuple[str, int]:
    host, port = text.rsplit(":", 1)
    return host, int(port)


def main() -> int:
    parser = argparse.ArgumentParser(description="Propriétaire gouttes — sans carte des hôtes")
    sub = parser.add_subparsers(dest="cmd")

    p_put = sub.add_parser("put")
    p_put.add_argument("--file", required=True)
    p_put.add_argument("--key", required=True)
    p_put.add_argument("--introducer", required=True, help="un seul host:port, pas le réseau")
    p_put.add_argument("--receipt", default="receipt.json")

    p_get = sub.add_parser("get")
    p_get.add_argument("--key", required=True)
    p_get.add_argument("--receipt", required=True)
    p_get.add_argument("--ticket-id", default=None)
    p_get.add_argument("--introducer", required=True, help="n'importe quel nœud encore vivant")
    p_get.add_argument("--output", required=True)

    args = parser.parse_args()
    if args.cmd == "put":
        return cmd_put(args)
    if args.cmd == "get":
        return cmd_get(args)
    parser.print_help()
    return 4


if __name__ == "__main__":
    sys.exit(main())
