---
type: Concept
id: prd-journal-v1
title: Journal de Prédiction — mesure de la fiabilité prédictive
description: Instrument de mesure de la capacité de Vagus OS à prédire les conséquences de ses propres actions. Boucle fermée prédiction → observation → écart → règle.
tags: [prediction, kpi, meta-apprentissage, boucle-fermee, argos]
owner: vagus
created_at: 2026-09-13
updated_at: 2026-09-13
version: 1.0
---

# Journal de Prédiction

## Problème résolu
Sans mesure, l'auto-évaluation de la fiabilité prédictive est de la croyance.
Hermes ne sait pas s'il se trompe de 5 % ou de 90 % sur les conséquences de ses
actions. Ce journal transforme cette croyance en chiffre.

## Principe
Toute action à conséquence **non triviale** (externe, irréversible, ou touchant
plusieurs nœuds du graphe) est précédée d'une prédiction **écrite** :

| Champ | Sens |
|---|---|
| `action` | ce qui va être exécuté |
| `prediction.expected` | ce que je pense qu'il va se passer |
| `prediction.impacts` | nœuds du graphe que je pense impacter |
| `prediction.confidence` | 0-1, mon niveau de confiance déclaré |
| `observation.actual` | ce qui s'est réellement passé |
| `observation.verified_at` | horodatage de la vérification |
| `delta.class` | exact / partial / wrong / surprise |
| `rule` | règle anti-récurrence si écart récurrent |

## Contrainte non négociable
La prédiction est écrite **avant** de connaître le résultat. Sinon on réécrit
l'histoire et la mesure ne vaut rien. Un écart non consigné est une occasion
d'apprentissage perdue (règle JP : jamais 2× la même erreur).

## Classes d'écart
- `exact` — prédiction conforme à l'observation
- `partial` — direction juste, ampleur ou périmètre faux
- `wrong` — direction fausse (le cas le plus instructif)
- `surprise` — conséquence non anticipée, hors du modèle

## KPI
- **Taux de justesse** = (exact + partial) / total — mesure la fiabilité globale
- **Taux de surprise** = surprise / total — mesure les trous du modèle du monde
  (c'est le KPI le plus important : une surprise = un angle mort structurel)
- **Biais de confiance** = moyenne(confidence) − taux de justesse — mesure la
  calibration. Positif = surconfiance, négatif = sous-confiance
- **Taux de couverture graphe** = prédictions dont les impacts ont été retrouvés
  dans le graphe / total — mesure si le graphe est assez riche pour prédire

## Points de mesure
- **J+7** — premier point. Fenêtre courte, mesures préliminaires.
- **J+30** — point de validation. Assez d'échantillons pour des tendances.

## Intégration
- Le graphe (`infra-graph.yaml`) alimente `prediction.impacts` : quand le graphe
  dit « cette action touche 3 nœuds », la prédiction devient vérifiable.
- Alimente la consolidation mémoire (`consolidation-daily.py`) : un écart
  récurrent devient une règle dans `rules/` ou un pitfall de skill.
- Règle H8 (dette technique) : une prédiction `wrong` non convertie en règle
  est une dette.

## Liens
- [Graphe d'infrastructure](infra-graph.md) — source des impacts prédits
- [Protocole de collaboration](../concepts/protocole-collaboration.md)
- [Journal log.md](../log.md) — consignation des écarts
