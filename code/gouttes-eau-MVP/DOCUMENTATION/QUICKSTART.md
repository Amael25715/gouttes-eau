# 🚀 QUICKSTART — Gouttes d'Eau (Clients Pilotes)

**Version :** 0.5-alpha  
**Temps estime :** 15 minutes  
**Pre-requis :** Python 3.10+, 1GB disque libre

---

## 1️⃣ Installation

git clone https://github.com/Amael25715/gouttes-eau.git
cd gouttes-eau
pip install -r requirements.txt
python code/gouttes_cli.py --version

---

## 2️⃣ Generer Vos Cles

python code/gouttes_cli.py genkeys --output ~/.gouttes-keys/

Resultat attendu :
- Private key: ~/.gouttes-keys/private.key (PERMISSIONS 600 !)
- Public key: ~/.gouttes-keys/public.key

IMPORTANT : Ne jamais partager private.key, sauvegarde public.key pour les autres clients

---

## 3️⃣ Configurer Votre Profil

# Fichier : config_client.yaml
client_id: "pilote_1"
storage_path: "./my_drops"
share_public_key: "~/.gouttes-keys/public.key"

---

## 4️⃣ Tester Encode

echo "Test Gouttes d'Eau - Pilot #1" > test_file.txt
python code/gouttes_cli.py encode --input test_file.txt --output ./my_drops --key ~/.gouttes-keys/private.key
ls -la ./my_drops/
# Attendu : 10 fichiers shard_0.dat a shard_9.dat + meta.json

---

## 5️⃣ Tester Decode

rm ./my_drops/shard_3.dat
python code/gouttes_cli.py decode --input ./my_drops --output ./restored --pubkey ~/.gouttes-keys/public.key
diff test_file.txt ./restored/test_file.txt
# Attendu : Aucun difference (succes)

---

## 6️⃣ Tester Limite de Tolerance

python code/gouttes_cli.py encode --input test_file.txt --output ./my_drops_fresh --key ~/.gouttes-keys/private.key
rm ./my_drops_fresh/shard_{1,3,5,7}.dat
python code/gouttes_cli.py decode --input ./my_drops_fresh --output ./restored_fresh --pubkey ~/.gouttes-keys/public.key
# Attendu : Succes (6 shards restants >= 6 minimum)

---

## 7️⃣ Tester ECHEC (comportement attendu)

python code/gouttes_cli.py encode --input test_file.txt --output ./my_drops_failure --key ~/.gouttes-keys/private.key
rm ./my_drops_failure/shard_{0,1,2,3,4}.dat
python code/gouttes_cli.py decode --input ./my_drops_failure --output ./restored_failure --pubkey ~/.gouttes-keys/public.key
# Attendu : ERREUR "Insufficient shards: 5/6 required"

---

## 8️⃣ Partager Votre Cle Publique

cat ~/.gouttes-keys/public.key > my_public_key.pub
# Envoyer a BEGO via Proton Mail (E2EE) Objet : "Gouttes d'Eau - Cle Publique - [VotreNom]"

---

## 9️⃣ Vérifier Santé du Système

python code/gouttes_cli.py verify --drops ./my_drops --pubkey ~/.gouttes-keys/public.key
# Attendu : All signatures valid, all hashes match

---

## 📝 Rapport de Test

Envoyer a BEGO :

Installation : PASS / FAIL
Key generation : PASS / FAIL
Encode test : PASS / FAIL
Decode with 1 loss : PASS / FAIL
Decode with 4 losses : PASS / FAIL
Decode with 5 losses : EXPECTED FAIL
Corruption detection : PASS / FAIL

Remarques : [Bugs rencontres, suggestions, difficultes]

---

## 🆘 Support

- Documentation complete : /docs/
- FAQ : /docs/FAQ.md
- Contact : BEGO via Proton Mail (E2EE)
- Bug report : GitHub Issues

**Bienvenue dans le programme pilote !**  
*Votre feedback faconne le systeme final.*
