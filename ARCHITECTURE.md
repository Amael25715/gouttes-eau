# Architecture – Gouttes d'Eau

## Objectif

Permettre la sauvegarde et le transfert de données de façon décentralisée, résiliente et sans point unique de contrôle.

## Principes d'alignement

- **Anti-pyramide** : aucun nœud n'est critique.
- **Cycles fermés** : les fragments restent dans le réseau ; la reconstruction ne dépend pas d'un centre.
- **Interdépendance** : chaque participant détient des gouttes des autres.
- **Fenêtre stase/chaos** : assez de redondance pour survivre aux pertes, pas assez pour centraliser.

## Codage d'effacement (correct)

Approche **par shards** (pas un simple découpage du message encodé) :

1. Les données sont organisées en **K shards de données**.
2. Pour chaque position (stripe), on calcule **M symboles de parité** via Reed-Solomon.
3. On obtient **N = K + M** gouttes.
4. **Toute combinaison de K gouttes** parmi N permet de reconstruire le fichier entier.
5. On peut donc **perdre jusqu'à M gouttes** sans perte d'information.

Paramètres POC par défaut : `K=6`, `M=4`, `N=10`.

## Preuve locale

```bash
pip install -r code/requirements.txt
python code/test_gouttes.py
```

Ou manuellement :

```bash
python code/fragmentation.py fragmenter mon_fichier.bin
python code/fragmentation.py perdre --n 4
python code/fragmentation.py reconstruire --out recupere.bin
cmp mon_fichier.bin recupere.bin
```

## Évolutions prévues

1. Échange réseau minimal (HTTP/sockets) entre 2 machines.
2. DHT pour localisation des gouttes.
3. Gros fichiers par blocs.
4. Indicateurs de résilience.

## Ce qu'on évite

- Liste centralisée de tous les nœuds.
- Envoi de tous les fragments à tout le monde.
- Dépendance à un serveur unique.
