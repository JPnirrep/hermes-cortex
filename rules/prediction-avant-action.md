---
type: Rule
id: rule-prediction-v1
title: Prédiction avant action — mesure et calibration
description: Toute action non triviale est précédée d'une prédiction écrite. La prédiction est écrite AVANT de connaître le résultat, sinon la mesure est nulle.
tags: [prediction, boucle-fermee, discipline, argos, meta-apprentissage]
owner: vagus
created_at: 2026-09-13
updated_at: 2026-09-13
version: 1.0
---

# Règle — Prédiction avant action

## Règle
Avant toute action **à conséquence non triviale** (action externe,
irréversible, ou touchant plusieurs nœuds du graphe), écrire la prédiction via
`tools/predict.py predict` :

```bash
python3 ~/hermes-cortex/tools/predict.py predict \
  --action "..." --expected "..." --impacts "..." --confidence 0.XX
```

Puis, après avoir **vérifié l'état réel** (pas supposé — vérifié), fermer :

```bash
python3 ~/hermes-cortex/tools/predict.py observe --id <id> \
  --actual "..." --class exact|partial|wrong|surprise
```

## Pourquoi
Sans mesure, la fiabilité prédictive est une croyance. Hermes ne sait pas s'il
se trompe de 5 % ou de 90 %. Le journal transforme cette croyance en chiffre,
et le chiffre en règle.

## Contrainte non négociable
La prédiction est écrite **avant** de connaître le résultat. Une prédiction
écrite après coup est une reconstruction, pas une mesure — elle détruit la
valeur de l'instrument.

## Ce qui déclenche l'obligation
- Action externe : envoi, publication, facturation, écriture hors VPS
- Action irréversible : suppression, purge, écrasement
- Action multi-nœuds : modification d'un fichier partagé, d'un secret, d'un service
- Modification structurelle : cron, service systemd, port, configuration

## Ce qui ne la déclenche pas
- Lecture, inspection, recherche
- Écriture réversible locale (fichier de travail, branche git)
- Tâche de session ordinaire

## Boucle fermée
1. Prédiction écrite
2. Action exécutée
3. État cible **relu** (jamais supposé)
4. Écart classé et consigné
5. Écart `wrong` ou `surprise` récurrent → règle anti-récurrence (règle H8)

Un écart non consigné est une occasion d'apprentissage perdue. JP : jamais 2×
la même erreur.

## Vérification automatique
Cron `predict-journal-check` (quotidien) : détecte les prédictions ouvertes
> 24 h (mesure perdue), l'obsolescence du graphe (config drift), et un taux de
surprise > 20 % (trous structurels du modèle).

## Liens
- [Journal de prédiction](../concepts/journal-prediction.md)
- [Graphe d'infrastructure](../concepts/infra-graph.md)
- [Règles Hermes Cortex](../index.md)
