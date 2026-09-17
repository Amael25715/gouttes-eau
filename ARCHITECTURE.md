# Architecture – Gouttes d'Eau

## Objectif

Sauvegarde et transfert décentralisés, résilients, sans point unique de contrôle.

## État d'avancement (honnête)

| Composant | Statut |
|-----------|--------|
| Fragmentation Reed-Solomon (shards K+M) | **Fait et testé** |
| meta.json + vérification hash | **Fait** |
| Tests auto + GitHub Actions | **Fait** |
| Échange réseau 2 nœuds | À faire |
| DHT / gossip | À faire |
| Chiffrement des gouttes | À faire (piste) |
| Déduplication source | À faire (piste) |

## Codage d'effacement

1. Données → **K shards** de données.
2. **M shards** de parité (Reed-Solomon, stripe par stripe).
3. **N = K + M** gouttes ; toute combinaison de **K** gouttes reconstruit le fichier.
4. POC : K=6, M=4, N=10 (on peut perdre jusqu'à 4 gouttes).

## Déduplication (piste, pas implémentée)

Préférence **à la source** :
- hash du contenu (ou par bloc) ;
- requête légère « qui a déjà ce hash ? » ;
- pas de réplication d'une base de dédup globale (anti-pyramide).

## Chiffrement (piste)

Option possible : chiffrement du contenu **avant** fragmentation (clé chez le propriétaire).  
Les nœuds stockent alors des gouttes opaques. À concevoir avec le flux réseau.

## Ce qu'on évite

- Liste centralisée de tous les nœuds
- Envoi de tous les fragments à tout le monde
- Dépendance à un serveur unique
