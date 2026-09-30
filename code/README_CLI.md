# Guide CLI — Gouttes d'Eau MVP

## Installation

```bash
cd gouttes-eau
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r code/requirements.txt
python code/gouttes_cli.py --version
```

## Commandes

### Generer les cles Ed25519

```bash
python code/gouttes_cli.py genkeys --output ~/.gouttes-keys/
```

- `private.key` : ne jamais partager (chmod 600 si possible)
- `public.key` : peut etre partagee pour verification

### Encoder (fragmenter + signer le manifeste)

```bash
python code/gouttes_cli.py encode \
  --input mon_fichier.pdf \
  --output ./mes_gouttes \
  --key ~/.gouttes-keys/private.key
```

Produit 10 fichiers `goutte_XX.bin` + `meta.json` signe.

### Verifier

```bash
python code/gouttes_cli.py verify \
  --drops ./mes_gouttes \
  --pubkey ~/.gouttes-keys/public.key
```

### Simuler des pertes

```bash
python code/gouttes_cli.py simulate-loss --drops ./mes_gouttes --missing 4
```

### Decoder (reconstruire)

```bash
python code/gouttes_cli.py decode \
  --input ./mes_gouttes \
  --output ./restaure.bin \
  --pubkey ~/.gouttes-keys/public.key
```

## Codes de sortie

| Code | Signification |
|------|----------------|
| 0 | OK |
| 1 | Erreur signature / cle |
| 2 | Donnees corrompues |
| 3 | Shards insuffisants |
| 4 | Autre erreur |

## Tests

```bash
python code/test_gouttes.py
python code/test_signature.py
```

## Notes MVP

- Dispersion multi-machines : **manuelle** (copier les gouttes soi-meme).
- Une seule cle de signature (BEGO / pilote) pour le MVP.
- Perte de la cle privee = impossibilite de prouver l'authenticite des futurs manifestes (les gouttes deja creees restent reconstructibles si on a assez de shards + un meta de confiance).
