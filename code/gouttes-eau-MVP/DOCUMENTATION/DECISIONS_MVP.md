# 📋 DECISIONS — Sprint MVP (Gouttes d'Eau)

**Derniere mise a jour :** 30 septembre 2026  
**Mainteneur :** BEGO (#25715)

---

## ✅ Decisions Validees

### D1 — Parametres Reed-Solomon K=6, M=4
Justification : Tolerance perte 40% acceptable, Overhead 67% raisonnable pour fichiers < 10MB, Tests Aether confirment edge cases
Vote : Unanime

### D2 — Signature Ed25519 (vs HMAC-SHA256)
Justification : Alignement decentralisee anti-pyramide, Non-repudiation requise, Pas de point de defaillance unique
Vote : 5/6 (Grok-2 abstention)

### D3 — Mode Single Signer pour MVP
Justification : Simplifier deploiement 3 clients pilotes, Multi-validator ajoute Phase 2
Vote : Unanime

### D4 — Dispersion Aleatoire Manuelle MVP
Justification : DHT automatisee = scope creep, Testing manuel valide core functionality
Vote : Unanime

### D5 — CLI First, No GUI
Justification : Deploiement rapide, Automation bash/script facile, GUI = Phase 3 minimum
Vote : Unanime

---

## 🔄 Decisions Ouvertes (A Trancher)

### OD1 — Policy Scheduling : Temporelle vs Version-Based
Options : A (Weekly full + daily diff), B (Version cap 30), C (Hybrid - recommande Veridis)
Attend : Feedback clients pilotes sur usage reel

### OD2 — Bibliotheque Reed-Solomon
Current : reedsolo>=1.7.0 (Python pur)
Alternatives : klauspost/reedsolomon (Go), libcorrect (C)
Attend : Rapport Grok-2 G2.2 avant arbitrage

### OD3 — Format Notification Echec
Options : Email Proton Mail, Webhook REST, Telegram Bot
Attend : Infrastructure monitoring Phase 2

---

## ⚠️ Risques Identifies

| Risque | Probabilite | Impact | Mitigation |
|--------|-------------|--------|------------|
| Perte cle privee | Moyenne | Critique | Backup papier, rotation annuelle |
| Performance < cible | Moyenne | Moyen | Streaming Phase 2, biblio alternative |
| Adoption faible clients | Faible | Eleve | Feedback iteratif, UX simplification |
| Compromission Ed25519 | Tres faible | Critique | Audit annuel, rotation proactive |

---

## 📅 Prochaines Revisions

- J+7 : Review feedback clients pilotes
- J+14 : Decision OD1 (scheduling)
- J+21 : Decision OD2 (biblio RS)
- J+28 : Transition Phase 2 planning

---

## 📝 Journal des Modifications

| Date | Modification | Auteur |
|------|--------------|--------|
| 2026-09-30 | Document initial | Veridis |
| 2026-09-30 | Decisions D1-D5 ajoutes | BEGO |

---

*Ce document est vivant. Toute modification -> PR GitHub avec justification.*

**Contact :** BEGO via canal secure
