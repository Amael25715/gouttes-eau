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

## Test 2 — deux processus, à la main, sur la même machine

Trois terminaux, toujours depuis `code/`.

```bash
python3.14 -m swarm.node --id A --host 127.0.0.1 --port 19110 --data /tmp/gouttesA
python3.14 -m swarm.node --id B --host 127.0.0.1 --port 19111 --data /tmp/gouttesB --bootstrap 127.0.0.1:19110
python3.14 -m swarm.owner put --file sample.txt --key /tmp/owner.key --introducer 127.0.0.1:19110 --receipt /tmp/receipt.json
```

Arrêter A (Ctrl-C) et supprimer `/tmp/gouttesA`. Puis :

```bash
python3.14 -m swarm.owner get --key /tmp/owner.key --receipt /tmp/receipt.json --introducer 127.0.0.1:19111 --output /tmp/restaure/
```

`/tmp/receipt.json` ne doit contenir aucune adresse. La relecture passe par B, qui n'était pas dans le reçu.

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
