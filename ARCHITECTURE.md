# Architecture – Gouttes d'Eau

## Objectif

Permettre la sauvegarde et le transfert de données de façon décentralisée, résiliente et sans point unique de contrôle.

## Principes d'alignement

- **Anti-pyramide** : aucun nœud n'est critique.
- **Cycles fermés** : les fragments restent dans le réseau ; la reconstruction ne dépend pas d'un centre.
- **Interdépendance** : chaque participant détient des gouttes des autres (logique lichens / symbiose).
- **Fenêtre stase/chaos** : assez de redondance pour survivre aux pertes, pas assez pour centraliser.

## Composants

### 1. Codage d'effacement (Reed-Solomon)
- Paramètres par défaut POC : K=6 (données nécessaires), M=4 (parité) → N=10 gouttes.
- On peut perdre jusqu'à M gouttes et reconstruire.
- À l'échelle : nombres adaptables (ex. K=16, M=8).

### 2. Placement des fragments
- POC actuel : local (dossier `gouttes/`).
- Cible : DHT (type Kademlia) + placement par hash du fragment.
- Chaque nœud ne connaît qu'un petit ensemble de voisins (pas de liste globale).

### 3. Découverte
- Bootstrap minimal (quelques adresses).
- Gossip léger pour la disponibilité.
- Pas de synchronisation d'état complet du réseau.

### 4. Métadonnées
- `meta.json` : hash original, taille, paramètres K/M/N, liste des gouttes + hash de chaque fragment.
- Permet la vérification d'intégrité avant reconstruction.

## Évolutions prévues

1. Découpage par blocs (gros fichiers).
2. Serveur / client minimal (sockets ou HTTP) pour échange de gouttes.
3. DHT pour localisation.
4. Indicateurs de résilience (taux de reconstruction réussie, dispersion réelle).

## Ce qu'on évite

- Liste centralisée de tous les nœuds.
- Envoi de tous les fragments à tout le monde.
- Dépendance à un serveur unique.
