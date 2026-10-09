# Gouttes — essaim minimal (preuve, pas la V2)

Ce dossier ne remplace pas `gouttes_cli.py`. C'est le palier d'après : plusieurs processus, une seule adresse d'entrée, récupération sans carte des hôtes.

Dans le dépôt : `code/swarm/`. Les commandes se lancent **depuis `code/`** (le dossier qui contient le paquet `swarm`).

## Test 1 — une seule commande

```bash
cd code
python3.14 -m swarm.demo
```

Attendu, dans cet ordre :

- `reçu sans adresse` (seulement `ticket_id` et `filename`)
- `aucun nœud n'a 6 gouttes de données`
- `nœuds 0..3 arrêtés et disques effacés`
- `gouttes manquantes : 4 (tolérance 4)`
- `OK` puis `OK hash ...`

Si une ligne manque, le test a échoué. Dépendances : `reedsolo` et `cryptography` (déjà dans `code/requirements.txt`).

## Test 2 — trois processus, à la main, sur la même machine

Deux hôtes ne suffisent pas. 10 gouttes réparties sur 2 machines font 5 et 5. En perdre 5 dépasse la tolérance de 4. Le message `gouttes manquantes : 5` est alors normal, pas un succès.

`sample.txt` n'est pas dans le dépôt. Il faut le créer.

Trois terminaux, depuis `code/`.

```bash
echo "test manuel" > /tmp/sample.txt
python3.14 -m swarm.node --id A --host 127.0.0.1 --port 19110 --data /tmp/gouttesA
python3.14 -m swarm.node --id B --host 127.0.0.1 --port 19111 --data /tmp/gouttesB --bootstrap 127.0.0.1:19110
python3.14 -m swarm.node --id C --host 127.0.0.1 --port 19112 --data /tmp/gouttesC --bootstrap 127.0.0.1:19110
```

C doit être démarré avant le `put`, sinon A ne le connaît pas. Puis, dans un quatrième terminal :

```bash
python3.14 -m swarm.owner put --file /tmp/sample.txt --key /tmp/owner.key --introducer 127.0.0.1:19110 --receipt /tmp/receipt.json
```

La ligne `répartition` doit indiquer qu'aucun hôte n'a plus de 4 gouttes. Arrêter A (Ctrl-C), supprimer `/tmp/gouttesA`, relire **via C** (le dernier démarré : il connaît A et B ; B peut ne pas connaître C) :

```bash
python3.14 -m swarm.owner get --key /tmp/owner.key --receipt /tmp/receipt.json --introducer 127.0.0.1:19112 --output /tmp/restaure/
```

Attendu : `gouttes manquantes : 4` ou moins, puis `OK`. Le reçu ne contient toujours aucune adresse.

## Test 3 — deux machines (seulement après les deux premiers)

`--host` doit être l'adresse **joignable** par l'autre machine (IP du LAN ou du VPN). `0.0.0.0` ne marche pas : c'est cette valeur qui est annoncée aux autres, et personne ne peut s'y connecter.

```bash
# machine A
python3.14 -m swarm.node --id A --host 192.168.1.10 --port 19110 --data ./dataA
# machine B, ne connaît que A
python3.14 -m swarm.node --id B --host 192.168.1.11 --port 19110 --data ./dataB --bootstrap 192.168.1.10:19110
```

Pas de NAT traversé par ce code. VPN d'abord si les machines ne se voient pas.

## Ce que le code ne fait pas

Pas de Shamir, pas de DHT, pas d'interface, pas de carte des hôtes. Au-delà d'une vingtaine de pairs, interroger tout le monde ne suffit plus. Le Reed-Solomon Python reste lent : la démo fait ~24 Ko, pas 15 Mo.
