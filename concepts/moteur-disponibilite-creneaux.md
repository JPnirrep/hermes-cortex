---
type: Concept
id: 12ea19c98f61
title: Moteur de créneaux — disponibilité, exceptions, anti-collision
timestamp: 2026-10-12
tags: [planification, disponibilite, creneaux, reservation, anti-collision, fuseaux, fenetres, idempotence]
links: [etudes-de-cas/2026-10-easyappointments-cartographie.md, concepts/efficience-tokens-pc-vps.md, rules/jp-workflow.md]
---

# Moteur de créneaux — disponibilité, exceptions, anti-collision

## Décision

Vagus OS retient une doctrine unique pour tout ce qui doit **placer une action dans le temps
d'une ressource rare** (rendez-vous, session, créneau de tournage, fenêtre d'appel API) :
une fonction pure de disponibilité + une re-vérification au moment de l'écriture.
Source : reverse engineering d'Easy!Appointments 1.6.0 sur instance réelle (voir l'étude de
cas liée). Sept règles, toutes vérifiées dans le code ou par probe HTTP.

## Les 7 règles

1. **Timeline unique avec drapeau.** Un seul enregistrement représente « occupé » :
   `start/end` + un booléen (`is_unavailability`). Un vrai rendez-vous, une indisponibilité
   interne, un blocage global et un événement importé d'un calendrier externe vivent dans la
   même table. Conséquence : **un seul** algorithme de soustraction, pas quatre.
2. **Plan par défaut + exceptions datées.** Le plan récurrent (jour de semaine → plage +
   pauses) est une donnée de la ressource ; les écarts ponctuels vont dans une table datée
   qui **remplace** le plan du jour (jamais ne s'y ajoute). Éviter de dupliquer le plan
   complet pour une seule journée modifiée.
3. **Pas de créneau ≠ durée.** Deux paramètres distincts : la longueur de l'action
   (`duration`) et le pas de la grille (`slot_interval`). Un RDV de 30 min peut se proposer
   toutes les 15 min.
4. **Fenêtres calculées dans le fuseau de la ressource**, pas du serveur : avance minimale
   (« on ne réserve pas à moins de 30 min ») et horizon maximal (« on ne réserve pas à plus
   de 90 jours ») se mesurent avec le fuseau de l'entité concernée.
5. **Re-vérification au commit (anti-collision).** Le calcul de disponibilité sert à
   *proposer* ; juste avant l'écriture, on **recalcule** et on exige que le choix demandé
   soit encore disponible. Vérifié : 8 réservations concurrentes sur le même créneau → 1
   seule acceptée. Sans cette règle, l'écriture devient un écrasement silencieux.
6. **Exclusion de soi-même.** Tout calcul de contrainte doit pouvoir exclure l'entité en
   cours d'édition, sinon repousser un rendez-vous de 15 min le rend « en conflit avec
   lui-même ».
7. **Résource résolue par capacité quand le demandeur s'en remet au système** : choisir
   l'entité sur un critère objectif et mesurable (« celle qui a le plus de créneaux libres »
   sur la plage demandée), puis revérifier la contrainte exacte. Jamais au hasard, jamais
   par affinité.

## Règle transversale (la plus coûteuse à oublier)

**Symétrie des gardes.** Quand un objet a plusieurs chemins d'écriture (interface publique,
API d'administration, script d'intégration, agent), **chaque** chemin doit porter le même
garde-fou. Cas observé : le chemin public refusait les collisions, l'API d'administration
les acceptait — une intégration peut donc casser ce que l'interface garantit. À poser comme
question d'audit pour tout livrable : *chaque chemin qui écrit la ressource passe-t-il par
le même garde ?*

Corollaire d'honnêteté technique : check-then-act n'est **pas** atomique. Une revérification
réduit la fenêtre, ne la ferme pas. Si la ressource est réellement critique : contrainte
d'unicité en base, verrou, ou file d'attente à consommateur unique.

## Conséquences opérationnelles chez nous

- Fenêtres peak/off-peak (arbitrage DeepSeek/glm) : passer d'une condition codée à un
  **plan + exceptions datées** (jour férié, déplacement ponctuel) sans redéployer.
- Écritures partagées PC↔VPS (`hermes-shared`) : revérifier l'état au dernier moment avant
  synchronisation, pas seulement à la lecture initiale. Nous avons le garde-fou d'écriture
  fail-closed, pas encore la revérification au commit.
- Actions à effet réel (envoi, publication, facturation) : idempotence par clé de dédup —
  nous savons ne pas *inventer* un résultat (`run-receipts`), nous ne savions pas encore
  formaliser le fait de ne pas *dupliquer* une action.
- Toute intégration qui écrit chez un tiers : exiger un point d'écriture unique gardé, ou
  refuser l'intégration.

## Ce que ce concept ne dit pas

Il ne dit rien de la récurrence, des ressources multiples par action (salle + personne),
ni du paiement — hors du périmètre observé chez Easy!Appointments. Ce sont des gaps
ouverts, pas des acquis.
