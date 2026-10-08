# Retour Aether sur le plan Veridis V2 — 8 octobre 2026

Le plan décrit un produit de trois mois. La demande de Bego est un test : N hôtes, chacun ne reconstruit pas le fichier d'un autre, une nouvelle installation ne connaît pas tout le réseau, le propriétaire relit **sans savoir où sont les gouttes**.

Plusieurs sections du plan contredisent cette demande. Je ne le prends pas comme base de code.

## Contre-exemples dans le plan

1. **Le propriétaire « ne sait pas où sont les gouttes » et le scénario 4 dit l'inverse.** « meta.json indique quels pairs ont quelles gouttes », puis « personne ne sait où sont toutes les gouttes ». Les deux phrases ne peuvent pas être vraies. Si le manifeste liste des IP, le propriétaire a une carte. S'il ne l'a pas, il faut une recherche par hash, pas une carte.

2. **`has_batches` dans la table de routage** dit à chaque nœud quels fichiers il héberge. C'est exactement la fuite à ne pas coder. Un nœud doit stocker un blob sous son hash, sans nom et sans index de batch.

3. **Shamir en sprint 1 ne répond pas au test.** Shamir partage la clé entre des humains. Reed-Solomon partage le fichier entre des hôtes. Mélanger les deux retarde le multi-hôtes et ajoute une procédure (qui a les parts, que se passe-t-il s'il en manque). La clé reste sur le propriétaire tant que le réseau ne marche pas.

4. **HKDF(mot de passe) n'est pas un stockage de clé.** Sans Argon2id (ou scrypt) avant, c'est un mauvais dérivé. Le plan le met dans le flux et reparle d'Argon2 seulement dans la checklist finale.

5. **Chiffrer `meta.json` entièrement** et en même temps s'en servir pour router : un nœud qui ne peut pas lire le manifeste ne peut pas s'en servir comme index. Le manifeste utile au propriétaire est un secret à lui. Les nœuds n'en ont pas besoin.

6. **Corps en base64 dans du JSON.** +33 % de taille et tout le fichier en mémoire. Le prototype joint envoie un en-tête court et un corps binaire.

7. **`curl http://…/health`** alors que le protocole décrit n'est pas HTTP. Deux services, ou aucun des deux. Pas les deux dans la même case.

8. **Réécriture en paquet `gouttes_eau/`.** Le CLI 0.5.1 est déjà testé par Bego (RS, signature, batch, nom de fichier). On n'y touche pas pour ce palier. Le réseau est un dossier à part.

9. **« 100 % de couverture »** n'est pas un livrable. Les tests qui passent sont un livrable. Le pourcentage ne l'est pas tant qu'il n'est pas mesuré.

10. **L'interface qui « montre où sont les gouttes »** annule le critère de succès. Un indicateur « au moins 6 gouttes joignables » oui. Une carte des IP, non.

11. **Les délais (0,5 jour pour HKDF, 10–13 semaines)** ne sont pas estimés à partir du code existant. Je ne les signe pas.

12. **Rôles.** Amael n'a pas à écrire `docker-compose`. Lumen n'a pas d'écran à dessiner tant que le CLI multi-hôtes n'a pas tourné sur deux vraies machines. Echo peut tenir la liste des tâches, pas inventer un Slack.

## Modèle retenu pour le test

| Qui | Ce qu'il a | Ce qu'il n'a pas |
|---|---|---|
| Propriétaire | clé 32 octets, `ticket_id`, **une** adresse d'un nœud vivant | la liste des gouttes en clair sur le disque des autres, la carte IP des gouttes |
| Nœud | blobs `sha256 → octets`, cache des pairs joignables | nom de fichier, clé, ordre des shards |
| Ticket (chiffré, répliqué) | hash des 10 gouttes, tailles, K/M | aucune adresse |

Recherche : le nœud d'entrée demande à chaque pair qu'il connaît « as-tu ce hash ? ». Avec 10 à 20 machines c'est suffisant et c'est prouvable. Une DHT (Kademlia) n'est justifiée qu'après, si le nombre de pairs dépasse ce que cette question coûte.

Connaissance minimale du réseau : le fichier de config d'un nouveau nœud contient **une** adresse (`--bootstrap`), pas dix. Après `HELLO`, il reçoit les pairs que l'introducteur connaît déjà. Il n'existe pas de registre central des fichiers.

Limite dite clairement : si **tous** les introducteurs connus sont morts et que personne n'a noté une autre adresse vivante, les données sont encore sur les disques mais plus adressables. Ce n'est pas « zéro adresse ». C'est « une adresse d'entrée, zéro adresse de goutte ».

## Ordre que je suis prêt à coder

| Étape | Quoi | Preuve | Pas avant |
|---|---|---|---|
| 0 (ce dossier) | 10 processus, chiffrement, recherche par hash, perte de 4 nœuds | `python -m swarm.demo` | — |
| 1 | Les mêmes commandes sur 2 puis 3 machines (LAN ou VPN) | `get` via l'autre machine, reçu sans IP de goutte | DHT, Shamir, UI |
| 2 | Second introducteur figé dans la config, redémarrage (le cache `peers.json` est déjà écrit) | tuer l'introducteur d'origine, relire | QUIC |
| 3 | Mesure RS sur 1 / 15 / 100 Mo. Si c'est trop lent, changer l'implémentation RS **sans** changer le format des hash | un chrono dans le README | réécrire le CLI 0.5.1 |
| 4 | Découpage en chunks quand l'étape 3 le montre | fichier de la taille du m4a déjà testé | index global |
| 5 | Écran, seulement s'il n'affiche pas la carte des hôtes | Lumen | — |

AES-GCM reste l'algorithme. Pas ChaCha « pour faire mieux ». Pas de TLS en plus **tant que** le corps est déjà chiffré et que le réseau est un LAN ou un VPN. TLS deviendra utile le jour où le `HELLO` circulera sur l'Internet ouvert (identité du nœud, pas le secret du fichier).

La signature Ed25519 du CLI 0.5.1 reste la sienne. Cet essaim n'en a pas besoin : l'intégrité d'une goutte est son hash, l'intégrité du fichier est le hash dans le ticket chiffré. Ajouter une signature sans une identité de propriétaire à vérifier serait du décor.

## Fichiers

- `swarm/protocol.py` — trame binaire
- `swarm/rs.py` — RS copié du POC (mêmes K/M)
- `swarm/box.py` — AES-GCM puis fragmentation
- `swarm/node.py` — stockage aveugle + pairs
- `swarm/owner.py` — `put` / `get`
- `swarm/demo.py` — la preuve 10 nœuds

Je pousse ce palier sur `Amael25715/gouttes-eau`, dossier `code/swarm/`, parce que Bego a demandé le code pour le tester. Le plan Veridis V2 n'y est pas.

