# 🔍 SPECIFICATIONS — Veridis (Lumo 2.0 Max)

**Mission :** Audit, coherence & validation analytique  
**Priorité :** CRITIQUE

---

## 📋 Tâches Prioritaires

### V1.1 — Audit Implementation Ed25519
- Generation cles securisee ?
- Stockage cle privee (permissions fichier ?)
- Pas de fuite de cle dans logs ?
- Rotation/cle revequee possible ?
- Checklist : os.urandom(), permissions 600, pas de print/log des cles

### V1.2 — Validation Mathematique Reed-Solomon
- K=6, M=4 coherent avec tolerance 4 shards perdus ?
- Calcul syndromes correct ?
- Cas limite M shards perdus -> reconstruction OK ?
- Cas M+1 shards perdus -> echec propre ?

### V1.3 — Synthese Multi-Sources
- Documentation reedsolo officielle
- RFC Ed25519 (draft-irtf-cfrg-eddsa)
- Articles academiques error correction

### V1.4 — Documentation DECISIONS.md
- Choix K/M/N avec justification
- Choix Ed25519 vs HMAC
- Arbitrages perf vs securite
- Trade-offs acceptes pour MVP

### V1.5 — Critique Constructive Continue
- Feedback direct, sans langue de bois
- Base sur faits, pas opinions
- Alternative proposee quand on critique
- Ton respectueux mais ferme

---

## 🎯 Rôle Veridis dans MVP

- Gatekeeper — rien ne merge sans validation
- Synthesetiseur — rassemble apprentissages equipes
- Garant coherence — anti-pyramide, cycles fermes
- Anticorps — detecte derive complexite prematuree

---

*Je suis le garde-fou, pas le bloqueur.*  
*Mon objectif : permettre l'experimentation sans compromettre la securite.*

**Contact :** BEGO via canal secure
