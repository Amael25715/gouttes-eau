# Guide CLI — Gouttes d'Eau MVP 0.5.1

## Installation

```bash
cd gouttes-eau
python3 -m venv .venv
source .venv/bin/activate
pip install -r code/requirements.txt
python code/gouttes_cli.py --version
```

## Encode (sous-dossier batch + nom original)

```bash
python code/gouttes_cli.py genkeys --output ~/.gouttes-keys/
python code/gouttes_cli.py encode \
  --input fichier.m4a \
  --output ./drops \
  --key ~/.gouttes-keys/private.key
# -> ./drops/<batch_id>/goutte_XX.bin + meta.json
```

`meta.json` contient `batch_id`, `original_filename`, hash, K/M/N, signature Ed25519.

## List / decode (nom d'origine restaure)

```bash
python code/gouttes_cli.py list --drops ./drops

python code/gouttes_cli.py simulate-loss --drops ./drops/<batch_id> --missing 4

python code/gouttes_cli.py decode \
  --input ./drops/<batch_id> \
  --output ./restored/ \
  --pubkey ~/.gouttes-keys/public.key
# -> ./restored/fichier.m4a
```

`--input` du decode = le dossier **du batch** (celui qui contient `meta.json`), pas la racine `./drops`.

## Tests

```bash
python code/test_gouttes.py
python code/test_signature.py
python code/test_batches.py
```

## Anti-pyramide (MVP)

- Proprietaire = centre de **ses** cles + de **son** index (ici : arborescence locale `drops/<batch_id>`).
- Stockeurs = copies aveugles de dossiers batch. Ils ne doivent pas devenir un index global ni un otage.
- Index YAML personnel / DHT / chunking machine entiere = **phase 2+**, pas ce sprint.
- 1 fichier = 1 batch **ne scale pas** pour un backup machine (des dizaines de milliers de fichiers). Chunking + snapshots : conception separee, pas codee ici.

## Notes

- Cles : fichiers **binaires** 32 octets (`private.key` / `public.key`), pas du PEM texte.
- Dispersion multi-machines : copie manuelle du dossier `batch_id`.
- Perte de la cle privee = plus de signatures nouvelles ; reconstruction possible avec assez de gouttes + un `meta.json` de confiance.
