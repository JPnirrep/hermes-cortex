---
type: Concept
id: aea4de9e84ec
title: Pattern — PGlite (Postgres embarqué) pour services légers
tags: [infra, postgres, sqlite, patterns, kleia-up, openmuse]
timestamp: 2026-09-26
owner: vagus
links: [pattern-lease-receipt.md, pattern-action-review.md]
source: CopilotKit/OpenMuse (@electric-sql/pglite ^0.3.14, MIT)
---

Troisième pattern retenu : **PGlite** — PostgreSQL compilé en WASM, tournant dans le processus Node, sans serveur ni conteneur.

## Pourquoi ça compte ici

Kleia-up a payé cher l'outillage SQLite : `nullslast()` (PostgreSQL-only) plantant sur SQLite, `from sqlalchemy.dialects.postgresql import UUID` cassant en dev, `.nullslast()` et autres fonctions de dialecte. Toute cette classe de bugs vient d'un décalage **dev SQLite / prod PostgreSQL**. PGlite supprime le décalage : même moteur, même dialecte, en dev comme en prod.

## Propriétés utiles

- **Zéro serveur** : aucun conteneur, aucun port à ouvrir. Adapté aux petits services, aux outils internes, aux scripts.
- **Même SQL que la prod Postgres** : les types (`jsonb`, `timestamptz`), les fonctions et les contraintes sont ceux de PostgreSQL.
- **Persistance fichier** : OpenMuse stocke tout dans `.openmuse/` — sauvegarde = copie de dossier.
- **Frontière nette** : PGlite ne peut PAS être ouvert par deux processus. Le dépôt le dit explicitement et bascule sur PostgreSQL dès qu'il faut un worker séparé. C'est une décision d'architecture à assumer, pas un détail.

## Où l'appliquer

- Petits services Vagus mono-processus (outils de veille, collecteurs, dashboards internes).
- Scripts qui ont besoin de vraies fonctions Postgres (`jsonb`, `timestamptz`, fenêtrages) sans monter une instance.
- Résoudre le décalage de dialecte sur les services **non-Kleia-up** ; pour Kleia-up lui-même (FastAPI + PostgreSQL déjà en place), l'intérêt est nul — la bascule coûterait plus qu'elle ne rapporte.
- **Règle Vagus** : service à processus unique → PGlite acceptable. Service multi-processus ou concurrent → PostgreSQL. Écrire cette décision dans la fiche du projet, pas dans la tête du praticien.

## Piège

Un `.sqlite` en dev et un Postgres en prod est une dette qui se paie en bugs de dialecte tardifs. Si un projet garde SQLite en dev, il doit assumer la contrainte : aucune fonction dialectale non standard, ou un garde-fou explicite par nom de dialecte. PGlite rend cette contrainte inutile — plus économique.

## Lien

- [Pattern — Bail SQL + Receipt](pattern-lease-receipt.md) : la bascule PGlite → PostgreSQL conditionne la possibilité de workers séparés.
- [Pattern — Action Review](pattern-action-review.md) : même famille de solutions (fiabilité d'exécution).

Source analysée : dépôt OpenMuse (MIT), commit 34b15bc, 26/09/26.
