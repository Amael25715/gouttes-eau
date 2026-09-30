# 📅 ARCHITECTURE — Scheduling Sauvegardes

**Version :** 0.1-draft  
**Statut :** Phase 2 (apres MVP)

---

## 🎯 Philosophy

Le systeme ne stocke pas la destination — il orchestre QUAND et COMMENT.
La dispersion est aleatoire, mais la configuration est centralisee (pour le mode Infra).

---

## 🕒 Strategies d'Ordonnancement

### Option A : Temporelle (Full/Differential)

schedule:
  full_backup:
    frequency: weekly
    day: sunday
    time: "02:00"
  differential_backup:
    frequency: daily
    exclude_days: [sunday]
    time: "03:00"

Avantages : Simple, aligne DevOps, facile a monitorer  
Inconvenients : Peut coincider avec pics charge, pas adaptatif

### Option B : Version-Based

version_policy:
  max_versions: 30
  retention_rule:
    - keep: 7 daily
    - keep: 4 weekly
    - keep: 12 monthly

Avantages : Historique precis, suppression automatique oldest-first  
Inconvenients : Plus complexe, necessite suivi etat precedent

### Option C : Hybride Recommandée

hybrid_policy:
  scheduled_full: weekly_sunday_02:00
  event_triggered:
    - detect_high_change_rate: threshold=20_percent
    - pre_deployment: tag="before_release"
  max_active_versions: 30

---

## 🔄 Versioning Logic

Version n+1 creee quand :
- Backup scheduled déclenche
- Changement detecte > seuil
- Tag manuel (event_before_deploy)
- Incident signale (tag_post_incident)

Suppression version quand :
- max_versions atteint -> supprime oldest
- older_than_retention_policy
- Commande manuelle admin (2/2 validators)

---

## ⚠️ Points de Vigilance

1. Ne jamais supprimer la derniere version
2. Test restauration mensuel
3. Notification echec immediate
4. Rotation cles annuelle

---

*Ce document evolue avec le feedback terrain.*  
*Suggestions de modifications -> DECISIONS.md*

**Mainteneur :** BEGO (#25715)
