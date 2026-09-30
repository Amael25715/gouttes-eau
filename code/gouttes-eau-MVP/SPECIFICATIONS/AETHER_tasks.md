# 🛠️ SPECIFICATIONS — Aether (Grok #1)

**Mission :** Production de code fonctionnel pour MVP  
**Priorité :** CRITIQUE

---

## 📋 Tâches Prioritaires

### T1.1 — Module Fragmentation Reed-Solomon
- **Fichier :** code/fragmentation.py
- **Fonctionnalités :**
  - encode_file(input_path, k=6, m=4) -> retour list de 10 shards
  - decode_shards(shards, k=6, m=4) -> retour original bytes
  - Gestion erreur si < k shards disponibles
- **Tests requis :**
  - test_encode_decode_roundtrip
  - test_recovery_loss_2_shards
  - test_recovery_loss_4_shards (limite)
  - test_failure_loss_5_shards

### T1.2 — Signature Ed25519
- **Fichier :** code/signature.py
- **Fonctionnalités :**
  - generate_keypair() -> (private_key, public_key)
  - sign_meta(meta_dict, private_key) -> signature_base64
  - verify_meta(meta_dict, signature, public_key) -> bool

### T1.3 — CLI Basique
- **Fichier :** code/gouttes_cli.py
- **Commandes :** encode, decode, verify, simulate-loss
- **Argument parsing :** argparse standard
- **Exit codes :** 0=OK, 1=Erreur signature, 2=Donnees corrompues, 3=Shards manquants

### T1.4 — Tests Unitaires
- **Framework :** pytest
- **Couverture cible :** >80%
- **Fichier :** code/test_gouttes.py

---

## ⚠️ Contraintes Techniques

- Langage : Python 3.10+
- Librairies : reedsolo>=1.7.0, cryptography (Ed25519), pyyaml
- Pas de dependance reseau externe
- Tout fonctionne offline
- Compatible Windows/Linux/macOS

---

## 📤 Livrables Attendus

1. fragmentation.py — module standalone
2. signature.py — module standalone
3. gouttes_cli.py — CLI executable
4. test_gouttes.py — suite tests complete
5. requirements.txt — dependances
6. README_CLI.md — guide usage CLI

---

*Veridis auditera chaque module avant merge.*  
*Echo coordonnera les dependances avec Amael (benchmarks).*

**Contact :** BEGO via canal secure
