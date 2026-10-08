"""Preuve locale : 10 nœuds, 4 tués, relecture via un survivant qui n'est pas dans le reçu.

Usage (depuis ce dossier) :
  python -m swarm.demo
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from swarm.protocol import rpc
from swarm.rs import sha256

ROOT = Path(__file__).resolve().parents[1]
N = 10
BASE = 19110
KILL = 4


def wait_ready(host: str, port: int, tries: int = 40) -> None:
    last = None
    for _ in range(tries):
        try:
            rpc(host, port, {"op": "HELLO", "role": "client"}, timeout=0.3)
            return
        except Exception as exc:  # noqa: BLE001 — attente de démarrage
            last = exc
            time.sleep(0.1)
    raise RuntimeError(f"{host}:{port} muet : {last}")


def main() -> int:
    work = Path(tempfile.mkdtemp(prefix="gouttes-swarm-"))
    procs: list[subprocess.Popen] = []
    try:
        sample = work / "sample.txt"
        payload = b"equilibre #25715\n" + b"abc123" * 4000
        sample.write_bytes(payload)
        key = work / "owner.key"
        receipt = work / "receipt.json"

        for i in range(N):
            data = work / f"node{i}"
            cmd = [
                sys.executable,
                "-m",
                "swarm.node",
                "--id",
                f"n{i}",
                "--host",
                "127.0.0.1",
                "--port",
                str(BASE + i),
                "--data",
                str(data),
            ]
            if i != 0:
                cmd += ["--bootstrap", f"127.0.0.1:{BASE}"]
            procs.append(
                subprocess.Popen(
                    cmd,
                    cwd=str(ROOT),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
            )
            wait_ready("127.0.0.1", BASE + i)

        for i in range(N):
            rpc("127.0.0.1", BASE + i, {"op": "REFRESH"}, timeout=3)

        put = subprocess.run(
            [
                sys.executable,
                "-m",
                "swarm.owner",
                "put",
                "--file",
                str(sample),
                "--key",
                str(key),
                "--introducer",
                f"127.0.0.1:{BASE}",
                "--receipt",
                str(receipt),
            ],
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        if put.returncode != 0:
            print(put.stdout)
            print(put.stderr, file=sys.stderr)
            return put.returncode

        body = json.loads(receipt.read_text(encoding="utf-8"))
        if any(k in body for k in ("host", "port", "peers", "address")):
            print("ECHEC : le reçu contient une adresse", body)
            return 2
        print(f"reçu sans adresse : {body}")

        # Chaque nœud ne doit pas détenir assez de gouttes de données pour reconstruire seul.
        # Le ticket est en plus, identique partout : on le compte à part.
        ticket_id = body["ticket_id"]
        for i in range(N):
            blobs = list((work / f"node{i}" / "blobs").glob("*"))
            data_blobs = [p for p in blobs if p.name != ticket_id]
            if len(data_blobs) >= 6:
                print(f"ECHEC : n{i} a {len(data_blobs)} gouttes de données")
                return 2
        print("aucun nœud n'a 6 gouttes de données")

        # Tuer l'introducteur d'origine et 3 autres. Relire via n9.
        for i in range(KILL):
            procs[i].terminate()
            procs[i].wait(timeout=5)
            shutil.rmtree(work / f"node{i}")
        print(f"nœuds 0..{KILL - 1} arrêtés et disques effacés")

        out = work / "restored.txt"
        get = subprocess.run(
            [
                sys.executable,
                "-m",
                "swarm.owner",
                "get",
                "--key",
                str(key),
                "--receipt",
                str(receipt),
                "--introducer",
                f"127.0.0.1:{BASE + N - 1}",
                "--output",
                str(out),
            ],
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        print(get.stdout)
        if get.returncode != 0:
            print(get.stderr, file=sys.stderr)
            return get.returncode
        if out.read_bytes() != payload:
            print("ECHEC : contenu différent")
            return 2
        print(f"OK hash {sha256(payload)}")
        print(f"preuve écrite sous {work}")
        return 0
    finally:
        for proc in procs:
            if proc.poll() is None:
                proc.terminate()
        for proc in procs:
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    sys.exit(main())
