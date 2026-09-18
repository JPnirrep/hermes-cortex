---
type: Concept
id: gate-semantique-non-testable
title: Non testable n'est pas non significatif — sémantique du verdict statistique
timestamp: 2026-09-12
tags: [gate, statistique, p-value, mcnemar, faux-negatif, semantique, verdict]
links: [concepts/gate-acceptation-skills-vagus.md, rules/jp-workflow.md]
---

# Non testable n'est pas non significatif

## Règle

Une p-value ne se lit que s'il existe des **paires discordantes** à tester. Quand
`b + c == 0` (gain ou perte identique sur toutes les tâches), le test exact de
McNemar renvoie `p = 1.0` **par construction**. Ce 1.0 signifie « aucun test
n'a été effectué », pas « aucun effet mesuré ». Confondre les deux transforme un
progrès total en rejet.

Conséquence : la p-value non applicable est marquée `null` avec
`p_status: non_applicable_gain_uniforme` — jamais simulée à 1.0, jamais décrite
comme « bruit ». Seul le delta tranche.

| Situation | Verdict | Motif |
|---|---|---|
| gain uniforme ≥ seuil | ACCEPT | p-value non applicable, seul le delta tranche |
| perte uniforme | REJECT | perte uniforme, aucune paire discordante |
| égalité | REJECT | aucun changement mesuré |
| gain uniforme < seuil | REJECT | effet trop faible pour être retenu |
| paires discordantes | test exact | significatif / bruit |

## Deuxième règle : un seuil est une politique, pas une mesure

`0.9 - 0.8` vaut `0.09999999999999998` en binaire. Sans tolérance, un gain
d'exactement le seuil de puissance est refusé comme « trop faible » — un faux
négatif produit par l'arrondi. Tolérance retenue : `1e-9`.

## Dette détectée au passage

L'ancien motif d'un rejet uniforme invoquait le seuil de puissance sur une
**perte** (`delta=-0.4 < seuil 0.1`), et annonçait « perte uniforme » sur une
simple **égalité**. Ces motifs sont la trace écrite que lira JP : un motif faux
est une décision non auditable. Vérifier la formulation d'un motif, pas
seulement le verdict.

## Lien

Corrige et complète `concepts/gate-acceptation-skills-vagus.md`. Le code vit
dans `skills/vagus-taste/scripts/taste_gate.py` (fonction pure
`decide_verbose`, 22 checks de selftest).
