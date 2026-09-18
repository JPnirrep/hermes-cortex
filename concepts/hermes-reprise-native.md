---
type: concept
id: 898ebf9ed88e
timestamp: 2026-08-12T22:30:00+02:00
tags: [hermes, runtime, reprise, replay, dette-technique, argos]
related:
  - skill:session-overflow-protocol
  - concepts:vagus-kg-v2.1
  - log:2026-08-12 (audit Muse Code)
---

# Reprise native Hermes — vérifier le runtime avant de construire

## Fait structurant
Le runtime Hermes dispose nativement d'un replay de session exact depuis state.db :
- `hermes chat --resume <session_id>` ou `-r latest` — reprise complète d'une session
- `hermes chat --continue <nom>` — reprise par nom / plus récente
- `hermes checkpoints` — snapshots fichiers (rollback write_file/patch/terminal), PAS replay de session
- `hermes sessions recover` — reconstruction d'une DB propre

## Règle dérivée
Avant de construire un script de checkpoint/reprise/backup maison : vérifier le natif (`hermes <cmd> --help`, sous-commandes sessions/checkpoints/backup). Construire un doublon = dette technique (H8). Corriger la procédure qui contourne le natif coûte moins cher que créer un mécanisme parallèle.

## Application
session-overflow-protocol v2 : Phase 5 = reprise native comme chemin principal ; synthèse manuelle < 300 chars reléguée en complément de contexte projet. [DETTE RESOLUE] le 12/08/2026.
