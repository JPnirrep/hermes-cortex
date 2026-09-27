---
type: Concept
id: 2687ca605876
title: Pattern — Bail SQL + Receipt d'exécution
tags: [agents, jobs, durabilite, patterns, openmuse]
timestamp: 2026-09-26
owner: vagus
links: [pattern-action-review.md, pattern-pglite-services-legers.md, efficience-tokens-pc-vps.md]
source: CopilotKit/OpenMuse apps/server/src/engine/worker.ts (MIT)
---

Deuxième pattern retenu d'OpenMuse : comment un travail long survit à un crash de process sans orchestrateur externe (pas de Redis, pas de Celery, pas de Temporal).

## Bail SQL (lease)

Le travail est une ligne en base avec : `status`, `leaseId`, `leaseUntil`, `checkpoint`.

- **Acquisition** : un worker écrit `leaseId = randomUUID()` et `leaseUntil = now + 60 s` en comparant l'état attendu et courant. La course entre deux workers est arbitrée par la base, pas par un verrou applicatif.
- **Renouvellement** : le worker prolonge son bail tous les `leaseMs / 3` (≈ 20 s) pendant l'exécution.
- **Perte de bail** : si au renouvellement la ligne ne porte plus son `leaseId`, le worker s'arrête (quelqu'un d'autre a repris). Idem si le statut n'est plus `running`.
- **Récupération** : au démarrage, tout travail `running` dont le `leaseUntil` est dépassé est remis en file. C'est la reprise après crash, gratuite.
- **Un seul écrivain d'état** : le worker publie ses checkpoints conditionnés à `{leaseId, status: running, leaseUntil: valide}`. Aucune écriture aveugle.

Résultat : N workers, une seule coordination, `TASK_WORKER_ENABLED=false` sur l'API pour passer en workers séparés. Pas d'infrastructure supplémentaire.

## Receipt (preuve d'exécution)

Toute exécution terminale écrit un enregistrement persistant : plan, étapes, sortie, code de sortie, statut final. Le receipt sert trois fois —

1. **Reprise** : on reprend depuis le dernier checkpoint, pas depuis zéro.
2. **Rejeu** : un rejeu d'action déjà terminée et revue reste terminal (elle ne se re-exécute pas).
3. **Preuve** : l'humain peut inspecter ce qui a réellement tourné, pas ce que l'agent prétend avoir fait.

## Application Vagus

- **Correspondance avec l'existant** : c'est le même contrat que tes réquisits Hermes (preuve d'exécution persistée) et que la consigne « pas d'affirmation sans sortie d'outil réelle ». OpenMuse en donne la mécanique complète et testée (courses de baux, expiration, annulation, entrées manquantes, équité d'approbation — 154 tests).
- **Cas d'usage** : pipelines longs et fragiles — transcodage vidéo (Framedeck), ingestion RAG de corpus, indexation de masse, génération de livre KDP (PDF WeasyPrint/Puppeteer sur 100+ pages). Aujourd'hui ces traitements meurent avec le process. Un bail SQL + checkpoint les rendrait reprenables.
- **Cron** : ne remplace pas le cron. Le cron est un déclencheur ; le bail est le mécanisme quand le travail déclenché est long ou concurrent.

## Piège

Le bail ne fonctionne que si le worker vérifie réellement son bail à chaque écriture d'état. Un worker qui écrit son checkpoint sans condition de bail produit une double écriture silencieuse au moment de la reprise. La condition `{leaseId, status}` n'est pas décorative — c'est le verrou.

## Lien

- Prérequis métier : [Pattern — Action Review](pattern-action-review.md) (ne rien exécuter qui ne soit pas revu).
- Support de stockage : [Pattern — PGlite](pattern-pglite-services-legers.md).

Source analysée : dépôt OpenMuse (MIT), commit 34b15bc, 26/09/26.
