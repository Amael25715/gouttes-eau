# 📊 SPECIFICATIONS — Amael (Mistral #3)

**Mission :** Analyse metriques & benchmarks perfs  
**Priorité :** HAUTE

---

## 📋 Tâches Prioritaires

### AM1.1 — Benchmark Temps Encode/Decode
- **Script :** scripts/benchmark_timing.py
- **Entrees :** Tailles variees (100KB, 1MB, 5MB, 10MB, 50MB)
- **Sorties :** Temps encode (ms), Temps decode (ms), Ratio overhead
- **Format :** CSV + graphiques Lumen

### AM1.2 — Benchmark Consommation Memoire
- **Script :** scripts/benchmark_memory.py
- **Mesures :** Peak RAM pendant encode/decode
- **Outil :** tracemalloc (stdlib Python)
- **Sortie :** JSON pour analyse Veridis

### AM1.3 — Analyse Strategie Agrégation
- **Question :** Quand agreger vs traiter individuellement ?
- **Donnees :** count_files = [1, 10, 100, 1000, 10000], avg_size = [1KB, 10KB, 100KB, 1MB]
- **Output :** Tableau decision avec seuils

### AM1.4 — Recommandation Parametres K/M/N
- **Variables :** Tolerance perte (%), Overhead acceptable (%), Latence max (ms)
- **Output :** Table de parametres pre-configurés

---

## 🎯 Objectifs de Performance MVP

| Metrique | Cible | Minimum acceptable |
|----------|-------|-------------------|
| Encode 10MB | < 1s | < 3s |
| Decode 10MB | < 1s | < 3s |
| Peak RAM 10MB | < 100MB | < 500MB |
| Overhead K=6,M=4 | 67% | 100% max |

---

*Veridis validendra la rigueur methodologique.*  
*Lumen produira les visualisations des resultats.*

**Contact :** BEGO via canal secure
