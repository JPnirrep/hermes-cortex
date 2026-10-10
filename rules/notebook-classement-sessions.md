---
type: rule
id: notebook-classe-001
timestamp: 2026-10-09
tags: [notebook, sujets, sessions, classement, hygiene, h1]
status: actif
links:
  - sujets/notebook-hermes-agents-solo/index.md
---

# Classement des sessions dans les sujets (Notebook)

## Règle

En FIN DE SESSION (moment H1 « sauvegarde / fin de session / synthétise / on reprend
plus tard »), toute session de travail doit être rattachée à UN sujet :

```bash
python3 ~/hermes-cortex/sujets/sujets.py lier <slug> <session_id> "<apport en 1 ligne>"
```

## Raisons

- Les conversations sont le principal flux de travail de JP : sans classement systématique,
  l'historique redevient une pile indifférenciée = doublons + travail refait (le problème
  initial que la couche sujets est censée résoudre).
- Une session = un seul sujet (anti-doublon). Le script refuse une session déjà liée ailleurs.
- Idempotent : relancer ne crée pas de doublon.

## Filet de sécurité hebdomadaire

```bash
python3 ~/hermes-cortex/sujets/sujets.py non-liees 25
```
Liste les sessions récentes sans sujet → les rattacher ou les écarter (sessions tmp, tests).

## Garde-fous

- Si aucun sujet ne correspond (score anti-doublon < 0,70 pour tout sujet existant) →
  proposer un titre de NOUVEAU sujet à JP avant création (plafond 15 sujets).
- Ne JAMAIS créer un sujet sans passer par `sujets.py check "<titre>"`.
- Les sessions `tmp` / scripts automatisés ne se classent pas (elles n'ont pas d'apport).
