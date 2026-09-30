# 🚀 PLAN MVP — Gouttes d'Eau (Sprint Test Terrain)

**Version :** 0.5-alpha  
**Date :** 30 septembre 2026  
**Mainteneur :** BEGO (#25715)  
**Clients pilotes :** 3 participants indépendants

---

## 🎯 Objectif du Sprint

Déployer un POC fonctionnel minimal chez 3 clients distincts pour valider :
1. Fragmentation Reed-Solomon (K=6, M=4, N=10)
2. Signature Ed25519 des metadonnees
3. Dispersion aleatoire entre stockage
4. Reconstruction fonctionnelle

**Horizon :** 4 semaines  
**Critere de succes :** Reconstruction reussie apres simulation perte de 3 shards

---

## 📦 Perimetre MVP

| Inclus | Hors perimetre |
|--------|----------------|
| CLI simple ligne de commande | Interface graphique |
| Signature locale unique (BEGO pour MVP) | Multi-validateurs complexes |
| Dispersion manuelle | DHT automatisee |
| Logs console simples | Monitoring centralise |
| Recovery manuel | Restauration automatique |
| Configuration YAML statique | Schedule dynamique |

---

## 👥 Roles pendant le MVP

| IA | Mission principale | Livraison attendue |
|----|-------------------|-------------------|
| **Aether** | Code CLI + tests | gouttes_cli.py fonctionnel |
| **Amael** | Benchmarks perf | Tableau temps/memoire par taille |
| **Echo** | Coordination taches | Checklist quotidienne |
| **Veridis** | Audit securite | Rapport critique Ed25519 |
| **Lumen** | Diagrammes | Flowchart usage client |
| **Grok-2** | Tests reproductibles | Scripts validation independants |

---

## 📅 Calendrier (4 Semaines)

| Semaine | Focus | Livrable |
|---------|-------|----------|
| **1** | Core fragmentation + signature | fragmentation.py valide |
| **2** | CLI basique + tests | gouttes_cli.py deployable |
| **3** | Deploiement 3 clients + feedback | Rapport terrain |
| **4** | Iteration sur retours | v0.6-beta ready |

---

## 🔧 Commandes MVP (CLI)

# Encodage
python gouttes_cli.py encode --input config.yaml --output ./drops --key ./private.key

# Decodage
python gouttes_cli.py decode --input ./drops --output ./restored --pubkey ./public.key

# Verification
python gouttes_cli.py verify --drops ./drops --pubkey ./public.key

# Simulation perte
python gouttes_cli.py simulate-loss --drops ./drops --missing 3

---

## 📋 Checklist Deploiement Client

- [ ] Cle Ed25519 generee (priv/pub)
- [ ] config.yaml personnalise
- [ ] Dossier ./drops cree avec 10 shards
- [ ] Reconstruction testee
- [ ] Simulation perte 2 shards OK
- [ ] Simulation perte 4 shards OK (limite)
- [ ] Simulation perte 5 shards ECHEC (normal)
- [ ] Feedback envoye a BEGO

---

## 🚨 Points de Vigilance MVP

1. Stockage non persistant — les drops ne sont pas repliquees automatiquement
2. Pas de schedule — declenchement manuel uniquement
3. Cle privee locale — perte = perte definitive des donnees
4. Dispersion manuelle — copier les shards soi-meme sur 3 machines

---

## ✅ Criteres Sortie MVP

Pour passer en Phase 2 :
- [ ] 3 clients ont reussi reconstruction sans erreur
- [ ] Temps encode/decode < 5s pour fichiers < 10MB
- [ ] Perte 4 shards = recuperation OK
- [ ] Perte 5 shards = echec propre (message clair)
- [ ] Retour clients collecte (tableau bugs/suggestions)

---

**Prochain meeting revue :** Semaine 4, Jour 5  
**Contact retour :** BEGO via Proton Mail (E2EE)

*Document genere par Veridis — Gardien de coherence*
