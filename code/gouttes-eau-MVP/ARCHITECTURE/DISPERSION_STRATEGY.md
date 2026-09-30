# 🌐 ARCHITECTURE — Dispersion Strategy

**Version :** 0.1-alpha  
**Statut :** Phase 1 (MVP)

---

## 🎯 Philosophie

"Aléatoire mais controle" — la dispersion suit des regles sans connaitre a lavance les destinations exactes.

---

## 🎲 Strategie de Dispersion

### Policy Random (MVP)
- Distribution aleatoire parmi nodes disponibles
- Assurer minimum 3 nodes utilises
- Eviter concentration sur un seul node

### Policy Weighted (Phase 2)
- Chaque node a capacite restante + sante
- Distribution proportionnelle aux weights

### Policy Geographic (Phase 3)
- Assurer diversite geographique
- Distribuer dans regions differentes

---

## 🔄 Regles de Survie

### Redondance Minima

| Shards totaux | Shards minimaux requis | Tolerance perte |
|---------------|----------------------|-----------------|
| 10 | 6 | 4 shards |
| 10 | 7 | 3 shards (mode haute securite) |
| 15 | 10 | 5 shards |

### Replication Transversale
- Shard 0 -> Client 1, Client 2, Client 3 (3 copies)
- Shard 1 -> Client 2, Client 3, Client 4 (3 copies)
- meme shard perdu, recuperable ailleurs

---

## 🚨 Recovery Scenario

SCENARIO : Client 2 tombe hors ligne
1. Detection heartbeat manquant > 5 minutes
2. Marquer shards Client 2 comme unreachable
3. Verifier shards restants : 10 - 4 = 6 -> OK
4. Reconstruction possible avec shards 0,1,3,5,7,9
5. Pendant reconstruction : generer nouveaux shards remplacments, distribuer sur clients 1,3,4,5

---

## ⚙️ Parametres Configurables

dispersion:
  algorithm: random_weighted
  min_unique_nodes: 3
  max_per_node: 3
  retry_failed_upload: 3
  timeout_seconds: 30

health_check:
  interval_seconds: 60
  timeout_seconds: 10
  retries_before_mark_unhealthy: 3

recovery:
  auto_rebalance: true
  rebalance_threshold: 50_percent_capacity
  priority: high

---

*La dispersion est la colonne vertebrale de la resilience.*  
*Plus de nodes = plus de survie.*

**Mainteneur :** BEGO (#25715)
