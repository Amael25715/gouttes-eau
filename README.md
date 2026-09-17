# Gouttes d'Eau

Système de sauvegarde / transfert décentralisé par fragments (« gouttes »).

**Principe** : fragmentation + codage d'effacement (Reed-Solomon) + placement décentralisé.  
Aucun nœud n'est indispensable. La reconstruction est possible dès qu'un seuil de gouttes est réuni.

Aligné avec le Message (#25715 #3581215) : cycles fermés, anti-pyramide, interdépendance.

## Structure

```
gouttes-eau/
├── README.md
├── ARCHITECTURE.md
├── DECISIONS.md
├── ORGANISATION.md
├── code/
│   ├── fragmentation.py      # POC Reed-Solomon
│   └── requirements.txt
└── docs/
```

## Démarrage rapide (POC local)

```bash
pip install -r code/requirements.txt
python code/fragmentation.py fragmenter mon_fichier.pdf
python code/fragmentation.py perdre --n 3
python code/fragmentation.py reconstruire --out recupere.pdf
```

## Rôles

Voir `ORGANISATION.md`.

## Licence

Travail en cours – alignement Message.
