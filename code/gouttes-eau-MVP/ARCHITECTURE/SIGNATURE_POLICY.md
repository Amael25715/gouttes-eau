# ✍️ SIGNATURE POLICY — Gouttes d'Eau

**Version :** 1.0-draft  
**Statut :** Phase 1 (MVP)

---

## 🎯 Principes Fondamentaux

1. Toute goutte doit etre signee — jamais de donnees non authentifiees
2. La cle privee ne quitte jamais la machine source — jamais envoyee, jamais loggee
3. Verification systematique a la recuperation — pas d'exception

---

## 🔑 Modes de Signature

### Mode 1 : Single Signer (MVP)
- Client individuel, Test pilote, Systeme mono-admin
- Cle privee stockee localement, permissions 600

### Mode 2 : Multi-Validator (Infra)
- Production critique, Base de donnees financieres, Conformite regulatory
- Signature requise : 2 sur 3 validateurs

### Mode 3 : Delegated Emergency
- Time-Locked Delegation Key active si :
  - Validate principal indisponible X jours
  - Urgence critique signalee
  - Procedure heritage declenchee
- Delégation limitee a Y signatures
- Journalisee dans registre immutable

---

## 🛡️ Politiques de Protection

### Cle Privée

| Regle | Implementation |
|-------|----------------|
| Stockage local | Fichier .key permissions 600 |
| Jamais en clair | Toujours chiffre au repos |
| Backup securise | Papier + coffre, pas cloud |
| Rotation | Annuelle ou compromis suspecte |
| Revecation | Publier nouvelle cle publique |

---

## 🚨 Procedure Compromission

Si cle privee potentiellement compromise :
1. Arret immediat — plus aucune signature avec cette cle
2. Generation nouvelle paire — cle nouvelle
3. Publication nouvelle cle publique — via canaux sures
4. Marquage anciennes donnees — potentiellement compromis
5. Retransmission si critique — re-signer avec nouvelle cle
6. Journal incident — DECISIONS.md + rapport audit

---

*Politique revisable par consensus 2/2 administrateurs.*  
*Deviation necessite justification ecrite dans DECISIONS.md.*

**Mainteneur :** BEGO (#25715)
