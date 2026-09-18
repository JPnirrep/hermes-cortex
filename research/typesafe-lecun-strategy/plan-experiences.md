# Plan d'expériences — Thèse binaire/typé × LeCun (BROUILLON, en attente panel R1-R5)

type: plan-experiences
timestamp: 2026-09-17
tags: [bench, typed-decisions, world-model, vagus]
liens: [typesafe-jev-analysis-2026-09]

## Hypothèses (pré-enregistrées avant toute mesure — anti-corruption)
- H1: la décomposition en questions typées bat le prompt monolithique sur les tâches Vagus (CUSTOS QC d'abord)
- H2: la confidence structurée de DeepSeek est informative (courbe de calibration non plate, Brier < baseline)
- H3: l'économie tokens/latence réelle >= 50% par cas de décision, sans perte d'accuracy
- H4 (R2): un journal prédiction/réalité sur les actions Vagus améliore le Brier score au fil des semaines

## Métriques communes
accuracy, faux négatifs (CUSTOS), tokens/cas (raisonnement vs livrable), latence p50/p95, €/cas, Brier/ECE, Brier prédictions d'actions

## Protocole anti-corruption
labels indépendants construits avant les runs; holdout 20%; 3 répétitions; runs hors heures de charge; harness mesuré lui-même; hypothèses figées ci-dessus

## Bras de comparaison
A: prompt monolithique (baseline actuelle) | B: workflow questions typées | C: B + confidence-gating | D: C + prédiction de conséquences

## Résultats
(à remplir après arbitrage panel)
