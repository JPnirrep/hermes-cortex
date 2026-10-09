# Étude de cas — Decommissioning d'un agent IA non fiable (Laya)

> Template réutilisable : dupliquer ce fichier par étude. Chaque section exige une
> preuve (chiffre, fichier, ID) — pas d'affirmation sans source interne.
> Usage : dossier commercial / crédibilité « nous avons fait, pas lu ».

## 1. Contexte
- **Système** : Laya, agent local de décision typée (classification de labels réels).
- **Rôle initialement visé** : doublure locale gratuite de JEV/TypeSafe (même API
  POST /v1/systemone, mêmes primitives décisionnelles).
- **Date de mise en service / d'arrêt** : arrêté le 28/09/2026.

## 2. Ce qui avait été promis (l'hypothèse de départ)
- Fit de calibration du 25/09 : ECE 0,137 — semblait excellent.
- Objectif : remplacer un appel API payant par une décision locale gratuite.

## 3. La mesure qui a tout dit (méthode, pas opinion)
Test en conditions réelles sur **603 labels réels** (jamais vus à l'entraînement) :
- **ECE réel : 0,80** (vs 0,137 au fit — ×5,8 de dégradation)
- **Accuracy au seuil 0,7 : 16,8 %** (vs constante "toujours la classe majoritaire" : 83,9 %)
- Verdict : **5,8× pire qu'une règle triviale**.
- Cause racine : le fit du 25/09 reposait sur 28 labels seulement — artefact
  statistique, pas capacité. Règle en découlant : ne pas publier de métrique
  sous le seuil de puissance statistique (< 30 items).

## 4. Décision et exécution
- **Décommissionnement complet le 28/09/2026** : le poste « décision typée » reste
  tenu par JEV/TypeSafe seul. Un SLM local = greffier (classif/extraction),
  JAMAIS décideur.
- Gains concrets : **8 Go libérés**, 2 crons supprimés (coût zéro maintenu),
  routeur nettoyé (transport_laya retiré).
- Archive réversible : `~/backups/laya-decommission-20260928/`.

## 5. Ce que ça prouve (l'argument client)
1. Nous mesurons la fiabilité de nos agents sur des données réelles, pas sur des démos.
2. Nous savons arrêter un agent qui ne marche pas — la plupart des systèmes ne le
   savent jamais (l'agent défaillant tourne en silence pendant des mois).
3. La boucle complète a été tenue : détection → mesure → décision → exécution →
   archive → règle anti-récurrence.
4. Coût de l'erreur évitée : si Laya était resté, chaque décision typée aurait eu
   ~83 % de chances d'être fausse.

## 6. Équivalent du pitch bootcamp
« Un agent IA, ce n'est pas un gadget » — non, et un agent IA qui semble marcher
sur 28 exemples et échoue à 16,8 % en production, c'est pire qu'un gadget : c'est
un risque. Notre système inclut le mécanisme qui le détecte et l'arrête.

---
## Champs à remplir pour la prochaine étude
- Nom du dispositif, dates, métrique avant/après, volume de données de test,
  cause racine, décision, gains (€/Go/temps), archive, lien règle anti-récurrence.
