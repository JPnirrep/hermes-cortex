---
id: 7a41c2e90bd5
type: Concept
title: Run Receipts — registre d'exécution des actions agent
description: Journal append-only YAML des actions à effet réel (qui, quoi, quand, résultat, coût, validation).
owner: vagus
updated_at: 2026-10-01
version: 1.0
tags: [gouvernance, tracabilite, agent, cout, audit]
links: [pattern-lease-receipt.md, rules/deny-rules.yaml, rules/facturation-cometapi-mimo.md]
---

# Run Receipts

## Problème

Les sessions Hermes produisent un registre de **coûts** (`state.db.sessions`,
`scripts/cost-report.py`) et un registre de **tâches planifiées** (`hermes cron runs`),
mais **aucun registre d'exécution unifié** répondant à : *telle action a-t-elle été
exécutée, sur quelle cible, avec quel résultat, approuvée par qui ?* Le coût ne dit pas
si l'action a réussi ; le cron ne dit pas ce qui a été fait hors cron.

C'est le chaînon manquant identifié en analysant la stack « Infinity OS »
(AI Impact, 30/09/2026) — leur seul apport réel : les *run receipts* (approvals,
budgets, record of who did what).

## Principe

Un **receipt** = un document YAML append-only, écrit à chaque action à effet réel :

```yaml
---
action: deploiement kleia-landing
actor: opencode            # antigravity | opencode | argos | cron | agent
approved: jp               # jp | auto (auto = action sans effet irréversible)
cost_usd: 0.012            # optionnel, si coût connu
note: 'PR: valide par JP 01/10/26'
receipt_id: 95966dfab89c
session: 5855
status: ok                 # ok | fail | partial
target: vps:8080
ts: '2026-10-01T13:52:03+02:00'
```

## Fichiers

- Journal : `~/hermes-cortex/logs/run-receipts.yaml` (multi-doc, append-only,
  versionné par le git quotidien du cortex)
- Santé machine-readable : `~/hermes-cortex/logs/run-receipts-health.json`
- Writer/lecteur : `~/.hermes/profiles/vagus/scripts/run_receipt.py`
  (`add` / `recent` / `audit`)
- Détecteur de panne : `~/.hermes/profiles/vagus/scripts/run_receipt_check.py`

## Discipline

**Un receipt s'écrit sur action à effet réel, pas sur lecture.** Déployer, publier,
envoyer, appeler une API payante, écrire une décision, modifier une config : receipt.
Lire un fichier, chercher, calculer : pas de receipt (le journal noierait le signal).

`status: fail` est une valeur normale et utile — le journal sert à *voir* les échecs,
pas à les cacher. Un `fail` non suivi d'un `ok` de rattrapage sur la même cible est
une anomalie de gouvernance.

## Cloison d'échec silencieux (règle C6)

Un registre qui n'écrit plus est un capteur mort : il reste muet, donc rassurant.
Le détecteur est un **second job** (cron Hermes `no_agent`, `0 */6 * * *`,
job `026c51ccdf6b`) qui n'émet une ligne que sur anomalie :

- `[ECRITURE]` journal absent ou YAML illisible
- `[CHAMP]` receipt sans champ requis (`ts`/`actor`/`action`/`status`)
- `[CADENCE]` sessions outillées sur 48 h mais zéro receipt sur la fenêtre
- `[MESURE]` journal vide depuis plus de 7 jours (le writer n'est jamais appelé)

Une anomalie d'écriture supprime les alertes dérivées : on signale la cause racine,
jamais des symptômes en cascade (sinon chaque corruption produit 3 alertes bruyantes).

## Ce que ça ne remplace pas

Le receipt **constate**, il ne **décide** pas. Le gate reste `rules/deny-rules.yaml`
(évalué avant l'action) ; le receipt est la trace après coup. Les deux sont
complémentaires : gate = prévention, receipt = preuve.
