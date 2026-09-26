---
type: Concept
id: laya-gate-suffisance-contexte
title: Gate de suffisance de contexte — Laya récusé en zero-shot, mécanique conservée
timestamp: 2026-09-25
tags: [laya, gate, suffisance, contexte, calibration, zero-shot, fine-tune, prism]
links:
  - concepts/laya-moteur-decisions-local.md
  - concepts/gate-acceptation-skills-vagus.md
  - concepts/gate-semantique-non-testable.md
  - rules/prediction-avant-action.md
---

# Gate de suffisance de contexte

## Le besoin

Avant d'appeler un LLM sur une tâche, décider si le **contexte fourni suffit** pour
l'exécuter. Trois issues : `lancer` (suffisant), `demander_info` (il manque un élément),
`escalade` (on ne sait pas juger). Cible : éviter les appels LLM sur contexte incomplet,
qui produisent des réponses plausibles et fausses.

## Mécanique livrée (conservée)

`~/.hermes/profiles/vagus/scripts/laya-adequacy-gate.py`
(`collect` | `predict` | `report` | `selftest`) — 10/10 checks verts.

Alignement strict sur la doctrine déjà validée, aucune invention parallèle :
- **corpus ancré sur données réelles**, aucune tâche synthétique (règle anti-biais JP) ;
- **égalité = rejet strict** — pas d'auto-satisfaction ;
- **p-value NON APPLICABLE** à paires uniformes (`None` + motif), jamais `1.0` simulée ni
  qualifiée de « bruit » (cf. `gate-semantique-non-testable`) ;
- tolérance virgule flottante `1e-9` (un seuil est une politique, pas une mesure) ;
- **aucune métrique publiée sous 30 labels** — un chiffre sous ce seuil est du bruit.

Décision opérationnelle : `conf ≥ 0,7` ET `p(suffisant) ≥ 0,5` → `lancer` ;
`< 0,5` → `demander_info` ; `conf < 0,7` → `escalade` (fail-closed).

## Résultat décisif — Laya récusé en zero-shot

**Test adversarial** : contexte long et bien habillé (CA + charges détaillées, analyse
marché, stratégie, objectifs) mais **salaires manquants** pour un calcul de marge.

| Cas | p(suffisant) | conf | Verdict du gate | Vérité |
|---|---|---|---|---|
| Contexte long, données clés absentes | **0,951** | 0,951 | lancer | **insuffisant** |
| Contexte court mais complet | 0,917 | 0,917 | lancer | suffisant |
| Contexte vide évident | 0,045 | 0,955 | demander_info | insuffisant |
| Contexte complet évident | 1,000 | 1,000 | lancer | suffisant |

**Laya se fait convaincre par l'apparence de suffisance** (volume, ton, vocabulaire
technique), pas par les faits. Les cas « réussis » ne l'étaient que parce qu'ils étaient
des évidences grossières rédigées par l'expérimentateur — les deux cas adversariaux
révèlent que la performance n'existe pas.

Cohérent avec l'avertissement des auteurs eux-mêmes : *« a fast base to specialise, not a
zero-shot decision engine »* (0,362 vs 0,318 au hasard). Aucun moteur zero-shot ne peut
juger une suffisance qu'il n'a jamais apprise.

## Décision

**Laya NON ADOPTÉ en zero-shot pour ce gate.** La mécanique (verdict, garde-fous,
journalisation, non-publication sous seuil) est conservée — elle est correcte et servira
au fine-tune. Le corpus est ouvert : `~/r4-bench/results/laya_adequacy.jsonl`, avec les
2 cas adversariaux enregistrés comme **tests de non-régression** du futur modèle.

## Ce qu'il faudrait pour que ça marche

1. ~200 paires réelles (contexte, tâche, suffisant/insuffisant), collectées en usage réel
   — pas rédigées pour l'occasion ;
2. fine-tune du checkpoint sur cette tâche (Laya est fait pour ça : « a fast base to
   specialise ») ;
3. ré-évaluation par le gate lui-même : `report` tranche via `decide_verbose` (gain de
   couverture significatif, McNemar exact).

Tant que 1-2 ne sont pas faits, **le gate ne décide rien** — il journalise.

## Leçon transposable

Un test dont les cas sont rédigés par l'expérimentateur mesure l'expérimentateur, pas le
modèle. Toute évaluation d'un moteur zero-shot doit inclure au moins un cas **adversarial**
où l'apparence contredit les faits — sinon on publie une performance qui n'existe pas.
