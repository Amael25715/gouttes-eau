"""Messages TCP : en-tête JSON + corps binaire. Pas de base64."""

from __future__ import annotations

import json
import socket
import struct

MAGIC = b"GTE1"
MAX_HEADER = 1_000_000
MAX_BODY = 64_000_000


class ProtocolError(Exception):
    pass


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ProtocolError("connexion fermée")
        buf += chunk
    return buf


def send_msg(sock: socket.socket, header: dict, body: bytes = b"") -> None:
    raw = json.dumps(header, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_HEADER or len(body) > MAX_BODY:
        raise ProtocolError("message trop grand")
    sock.sendall(MAGIC + struct.pack(">I", len(raw)) + raw + struct.pack(">I", len(body)) + body)


def recv_msg(sock: socket.socket) -> tuple[dict, bytes]:
    magic = _recv_exact(sock, 4)
    if magic != MAGIC:
        raise ProtocolError("magic invalide")
    hlen = struct.unpack(">I", _recv_exact(sock, 4))[0]
    if hlen > MAX_HEADER:
        raise ProtocolError("entête trop grand")
    header = json.loads(_recv_exact(sock, hlen).decode("utf-8"))
    blen = struct.unpack(">I", _recv_exact(sock, 4))[0]
    if blen > MAX_BODY:
        raise ProtocolError("corps trop grand")
    body = _recv_exact(sock, blen) if blen else b""
    return header, body


def rpc(host: str, port: int, header: dict, body: bytes = b"", timeout: float = 2.0) -> tuple[dict, bytes]:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        send_msg(sock, header, body)
        return recv_msg(sock)
