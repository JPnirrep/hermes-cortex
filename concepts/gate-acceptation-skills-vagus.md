---
type: Concept
id: gate-acceptation-skills-vagus
title: Porte d'acceptation statistique des skills (portée de WikiSkill)
timestamp: 2026-09-12
tags: [gate, gating, wikiskill, skills, auto-evolution, mesure, mcnemar, vagus-taste]
links: [rules/jp-workflow.md, concepts/gate-semantique-non-testable.md]
---

# Porte d'acceptation statistique des skills

## Décision (12/09/2026, JP : « Option2 go »)

Reprendre de `ashutoshsinghpr7/wikiskill` (implémentation réelle du papier
arXiv:2608.27454) **uniquement la mécanique de gating**, pas le simulateur de
tâches synthétiques. Portée dans `skills/vagus-taste/scripts/taste_gate.py`.

## Règle

```
ACCEPT  <=>  R_val > R_best  ET  (p <= alpha OU gain uniforme)  ET  delta >= delta_min
REJECT  sinon — patterns consignés, jamais rollbackés
```

**Non testable ≠ non significatif** : sur un gain uniforme, McNemar renvoie
p=1.0 par construction et la p-value est marquée non applicable. Détail et
correction : `concepts/gate-semantique-non-testable.md`.

- `p` = p-value exacte bilatérale sur paires discordantes (McNemar exact), sans
  dépendance externe.
- Égalité = rejet (strict). Un label comparé à lui-même est refusé — pas
  d'auto-satisfaction possible.
- Corpus ancré sur données réelles : 36 cas du golden dataset OMP + les
  corrections utilisateur (`taste_signals.jsonl`). Aucune tâche synthétique.

## Pourquoi

Avant : un skill était modifié à dire d'expert ou après incident, jamais mesuré.
Une évolution pouvait dégrader le système sans détection. Le gate ajoute la
mesure A/B avant acceptation. Il ne produit aucun skill — il tranche.

## Limite assumée

`run_task()` n'est pas branché hors ligne : les scores viennent d'un scorer
déterministe qui répète la mécanique et les tests. Une mesure réelle exige un
runner Hermes isolé (`hermes chat --oneshot` + `HERMES_HOME` dédié au snapshot,
cf. `harness.py` amont). Tant que ce n'est pas fait, la porte teste la
mécanique, pas la qualité d'un skill — ne jamais présenter un ACCEPT dry-run
comme une preuve de qualité.

## Traçabilité amont

Épinglé sur le commit `02fac2c804fe156e43b12c691e4ae527614d63a1` (MIT).
Cron `vigie-wikiskill-derive` (07h00, `no_agent`, 0 €) alerte si l'amont bouge.

## Lien

S'alimente des corrections détectées par `vagus-taste` (§Action Directe,
§quand détecter un signal). Une correction non consignée dans
`taste_signals.jsonl` est une correction qu'on ne pourra jamais mesurer.
