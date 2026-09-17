# Gouttes d'Eau

Système de sauvegarde / transfert décentralisé par fragments (« gouttes »).

**État actuel** : POC **local** prouvé (Reed-Solomon par shards).  
Pas encore de DHT, gossip, ni échange multi-machines dans le code.

Aligné Message (#25715 #3581215) : cycles fermés, anti-pyramide, interdépendance.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r code/requirements.txt
python code/test_gouttes.py
```

## Usage POC local

```bash
python code/fragmentation.py fragmenter mon_fichier.pdf --out gouttes
python code/fragmentation.py perdre --dossier gouttes --n 4
python code/fragmentation.py reconstruire --dossier gouttes --out recupere.pdf
cmp mon_fichier.pdf recupere.pdf
```

## Structure réelle

```
gouttes-eau/
├── README.md
├── ARCHITECTURE.md
├── DECISIONS.md
├── ORGANISATION.md
├── code/
│   ├── fragmentation.py
│   ├── test_gouttes.py
│   └── requirements.txt
└── .github/workflows/test-gouttes.yml
```

## Prochaines briques (pas encore codées)

1. Échange réseau minimal entre 2 processus / machines
2. Déduplication à la source (requête par hash, sans base globale)
3. Chiffrement optionnel des gouttes
4. DHT / gossip à plus grande échelle
