---
type: Concept
id: pi-executeur-frugal
title: Pi en exécuteur frugal sandboxé (VPS)
timestamp: 2026-10-30
tags: [pi, earendil-works, executeur, sandbox, docker, frugalite, tokens, vps, workflow]
links: [concepts/agent-plugin-standard.md, decisions/, concepts/custos-doctrine.md]
---

# Pi en exécuteur frugal sandboxé (VPS)

## Décision

Pi 1.4.0 (Earendil Works, MIT) est installé sur le VPS dans une **image Docker durcie**
(`pi-sandbox:1.4.0`, 321 Mo) et exposé par le lanceur `/home/debian/.local/bin/pi-sbx`.

Rôle : **bras mécanique token-lean**, pilotable par Hermes. Il **ne remplace pas** Hermes
(qui garde recherche, synthèse, rédaction, stratégie).

Cohérent avec l'audit du 26/10 : « non pertinent comme remplaçant, pertinent comme source
de patterns » → ici le pattern est industrialisé en outil.

## Chiffres mesurés (30/10/2026, VPS OVH)

| Métrique | Valeur |
|---|---|
| RAM crête sandbox | ~46 MiB (polling) — 125 MiB en natif |
| Durée tâche simple | 2,9 – 5,7 s |
| Tokens facturables | ~6,2 k (dont ~5,7 k cacheRead) |
| Coût / tâche | 0,0005 – 0,0009 $ |
| Modèle | `deepseek-flash` (ctx 1 M, $0,30/M in, $1,20/M out) |
| RAM au repos | 0 (conteneur à la demande, aucun daemon) |

## Garde-fou

Pi n'a **aucune permission intégrée** : le binaire `pi` nu a un accès total au système.
L'usage passe **obligatoirement** par `pi-sbx` :
`--read-only`, tmpfs jetables, 512 Mo / 1 CPU / 256 pids, `no-new-privileges`,
utilisateur non-root, seul `$PWD` monté, clé API en env (jamais dans l'image).

## Limites

- Sur micro-tâches, `:low`/`:max` ne changent presque rien au coût → garder `high`.
- Plus de tours qu'OpenCode sur tâches longues (compensé par coût/tour très faible).
- Étape 2 non faite : délégation Hermes → Pi via `--mode rpc` sur une recette métier réelle.
