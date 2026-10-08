"""Nœud de stockage. Il garde des blobs opaques indexés par hash. Il ne connaît pas les fichiers.

Découverte : une adresse d'introduction, puis échange de pairs. Pas de liste de gouttes.
"""

from __future__ import annotations

import argparse
import json
import socketserver
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from swarm.protocol import ProtocolError, rpc, recv_msg, send_msg
from swarm.rs import sha256

GET_TIMEOUT = 0.6


class Node:
    def __init__(self, node_id: str, host: str, port: int, data: Path, bootstrap: tuple[str, int] | None):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.data = data
        self.blobs = data / "blobs"
        self.blobs.mkdir(parents=True, exist_ok=True)
        self.bootstrap = bootstrap
        self._lock = threading.Lock()
        self.peers: dict[str, tuple[str, int]] = {}
        self._load_peers()

    def _peers_path(self) -> Path:
        return self.data / "peers.json"

    def _load_peers(self) -> None:
        path = self._peers_path()
        if not path.exists():
            return
        raw = json.loads(path.read_text(encoding="utf-8"))
        for item in raw:
            self.peers[item["id"]] = (item["host"], int(item["port"]))

    def _save_peers(self) -> None:
        items = [{"id": i, "host": h, "port": p} for i, (h, p) in self.peers.items()]
        self._peers_path().write_text(json.dumps(items), encoding="utf-8")

    def remember(self, node_id: str, host: str, port: int) -> None:
        if node_id == self.node_id:
            return
        with self._lock:
            self.peers[node_id] = (host, int(port))
            self._save_peers()

    def peer_list(self) -> list[dict]:
        with self._lock:
            items = [{"id": self.node_id, "host": self.host, "port": self.port}]
            for i, (h, p) in self.peers.items():
                items.append({"id": i, "host": h, "port": p})
        return items

    def has(self, drop_id: str) -> bool:
        return (self.blobs / drop_id).is_file()

    def read(self, drop_id: str) -> bytes:
        return (self.blobs / drop_id).read_bytes()

    def store(self, drop_id: str, body: bytes) -> None:
        if sha256(body) != drop_id:
            raise ValueError("drop_id != sha256(corps)")
        path = self.blobs / drop_id
        if not path.exists():
            path.write_bytes(body)

    def refresh_from_bootstrap(self) -> int:
        if not self.bootstrap:
            return len(self.peer_list())
        host, port = self.bootstrap
        if (host, port) == (self.host, self.port):
            return len(self.peer_list())
        header, _ = rpc(
            host,
            port,
            {
                "op": "HELLO",
                "role": "node",
                "id": self.node_id,
                "host": self.host,
                "port": self.port,
            },
            timeout=2.0,
        )
        self._absorb(header.get("peers", []))
        return len(self.peer_list())

    def _absorb(self, peers: list[dict]) -> None:
        for item in peers:
            self.remember(item["id"], item["host"], int(item["port"]))

    def find(self, drop_id: str) -> bytes | None:
        if self.has(drop_id):
            return self.read(drop_id)
        peers = [(h, p) for h, p in ((i["host"], i["port"]) for i in self.peer_list()) if (h, p) != (self.host, self.port)]
        if not peers:
            return None

        def ask(addr: tuple[str, int]) -> bytes | None:
            try:
                header, body = rpc(addr[0], addr[1], {"op": "GET", "drop_id": drop_id}, timeout=GET_TIMEOUT)
            except (OSError, ProtocolError, TimeoutError, json.JSONDecodeError):
                return None
            if header.get("op") == "DATA" and body and sha256(body) == drop_id:
                return body
            return None

        with ThreadPoolExecutor(max_workers=min(8, len(peers))) as pool:
            futures = [pool.submit(ask, addr) for addr in peers]
            for fut in as_completed(futures):
                data = fut.result()
                if data is not None:
                    return data
        return None


class Handler(socketserver.BaseRequestHandler):
    node: Node

    def handle(self) -> None:
        self.request.settimeout(30)
        try:
            header, body = recv_msg(self.request)
        except (ProtocolError, json.JSONDecodeError, TimeoutError, OSError):
            return
        op = header.get("op")
        try:
            if op == "HELLO":
                if header.get("role") == "node":
                    self.node.remember(header["id"], header["host"], int(header["port"]))
                send_msg(self.request, {"op": "PEERS", "peers": self.node.peer_list()})
            elif op == "REFRESH":
                count = self.node.refresh_from_bootstrap()
                send_msg(self.request, {"op": "OK", "peers": count})
            elif op == "PUT":
                self.node.store(header["drop_id"], body)
                send_msg(self.request, {"op": "OK"})
            elif op == "GET":
                drop_id = header["drop_id"]
                if self.node.has(drop_id):
                    send_msg(self.request, {"op": "DATA", "drop_id": drop_id}, self.node.read(drop_id))
                else:
                    send_msg(self.request, {"op": "MISS"})
            elif op == "FIND":
                data = self.node.find(header["drop_id"])
                if data is None:
                    send_msg(self.request, {"op": "MISS"})
                else:
                    send_msg(self.request, {"op": "DATA", "drop_id": header["drop_id"]}, data)
            else:
                send_msg(self.request, {"op": "ERR", "error": "op inconnue"})
        except Exception as exc:  # protocole : renvoyer l'erreur, ne pas tuer le nœud
            try:
                send_msg(self.request, {"op": "ERR", "error": str(exc)})
            except OSError:
                pass


def serve(node: Node) -> socketserver.ThreadingTCPServer:
    class Bound(Handler):
        pass

    Bound.node = node

    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    server = Server((node.host, node.port), Bound)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="Nœud gouttes (stockage aveugle)")
    parser.add_argument("--id", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--bootstrap", default="", help="host:port de l'introducteur, vide si on EST l'introducteur")
    args = parser.parse_args()
    bootstrap = None
    if args.bootstrap:
        host, port = args.bootstrap.rsplit(":", 1)
        bootstrap = (host, int(port))
    node = Node(args.id, args.host, args.port, Path(args.data), bootstrap)
    if bootstrap:
        node.refresh_from_bootstrap()
    server = serve(node)
    print(f"nœud {node.node_id} écoute {node.host}:{node.port} blobs={node.blobs}", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
