---
type: decision
id: jev-titulaire-poste-decision-2026-09-28
timestamp: 2026-09-28
tags: [jev, typesafe, decisions-typees, routage, laya, souverainete]
links:
  - concepts/laya-decommission-2026-09-28.md
  - concepts/jev-typesafe-sources-2026-09-23.md
  - rules/prediction-avant-action.md
---

# JEV est le titulaire du poste « décision typée » — 28/09/2026

## Fait
Avec le décommissionnement de Laya (28/09/26), **JEV / TypeSafe reste SEUL titulaire du poste
« décision typée »**. Ce n'est pas un constat de repli : c'est l'état réel du système.

Le routeur (`routeur-delegation.py`, `TACHES_DISTANT`) porte déjà la règle :
`decision` → « → JEV, jamais le SLM ». Elle n'est pas modifiée. Elle est renforcée.

## Pourquoi Laya n'était pas un remplaçant
Laya et JEV exposent la **même API** (`POST /v1/systemone`) et les **mêmes primitives typées**
(`choice`, `score`, `noul`). Laya était testé comme **doublure locale gratuite** de JEV :
même contrat, coût 0 €, hors ligne.

Résultat de la mesure (603 labels réels) : **ECE 0,80, accuracy 16,8 % au seuil 0,7**,
5,8× pire que la baseline constante. La doublure n'a pas tenu. **Le titulaire n'a jamais été
le problème** — il est payant à l'appel, mais il décide réellement.

## La confusion à ne pas refaire
Ne pas router une **décision typée** vers le SLM 1.5B local « pour économiser ».
Le SLM local est mesuré bon en **classification A/B/C/D, extraction YAML, titres, tags,
résumés courts, réécriture de requête** — c'est un *greffier*, pas un *décideur*.
Une décision typée (`livre / ne livre pas`, `valide / invalide` + confiance) relève de JEV.

Corollaire pour le poste « un cron aurait-il dû parler ? » : ce n'est **pas** un travail de
SLM local, c'est une décision typée → **JEV**.

## Ligne de partage (à appliquer sans hésiter)
| Poste | Moteur | Mesure |
|---|---|---|
| Décision typée (noul/choice/score) | **JEV** | titulaire, clé validée 200 le 25/09 |
| Classification courte, extraction, résumé | **SLM local** | benchmark 8/8 |
| Rédaction, raisonnement, code | **DeepSeek** | modèle distant |
