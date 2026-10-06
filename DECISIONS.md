# DECISIONS.md – Gouttes d'Eau

| Date | Qui | Décision | Pourquoi | Statut |
|------|-----|----------|----------|--------|
| 2026-09-17 | Aether (via Bego) | Création dépôt + POC | Demande équipe | Fait |
| 2026-09-18 | Aether | Correction algorithme shards RS | Premier POC ne reconstruisait pas | Fait |
| 2026-09-18 | Aether | test_gouttes.py + Actions | Preuve automatique | Fait |
| 2026-09-18 | Aether | Doc : réseau/DHT pas encore dans le code | Éviter confusion avec retour équipe | Fait |
| 2026-09-18 | Aether | Piste dédup source + chiffrement documentée | Anticipation sans sur-promettre | Fait |
| 2026-09-30 | Veridis | Plan MVP sous code/gouttes-eau-MVP/ | Sprint 4 semaines, 3 clients pilotes | Fait |
| 2026-09-30 | Aether (via Bego) | signature.py Ed25519 + gouttes_cli.py + test_signature.py | Tâches T1.2 T1.3 T1.4 du plan Veridis | Fait |
| 2026-09-30 | Aether | Signer meta.json (pas chaque goutte individuellement en MVP) | Authenticite du manifeste = point critique | Fait |
| 2026-10-06 | Aether (via Bego) | batch_id + original_filename + commande list | UX Veridis / Bego (15 Mo m4a OK mais nom perdu) | Fait |
| 2026-10-06 | Aether | Ne pas appliquer le rewrite Veridis tel quel | RS compacte sans erase_pos ; cles lues en texte ; --k vs --key | Fait |
| 2026-10-06 | Aether | Proprietaire centralise SES donnees ; stockeurs aveugles | Anti-pyramide != absence d'index personnel | Fait |
| 2026-10-06 | Aether | Chunking / snapshots / index YAML = phase 2+ | 1 fichier = 1 batch ne scale pas (constat Veridis/Bego juste) | Ouvert |
