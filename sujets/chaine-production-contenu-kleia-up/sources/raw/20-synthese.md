---
type: synthese-college
id: college-crea-gestion-creation-20261009
title: Collège agentique — chaîne de production de contenu Sandrina/Kleia-up
owner: JP
statut: à valider (rien exécuté)
date: 2026-10-09
moteurs: [qwen3.7-max, mimo-v2.6-pro, grok-4.3, mimo-v2.6-flash/minimax-m2.7, o4-mini]
tags: [kleia-up, sandrina, production, n8n, kanban, college-agentique, arbitrage]
links:
  - sandrina-strategie/PLAN-SEMAINE-5-9-OCTOBRE.md
  - sandrina-strategie/LIGNE-EDITO-REWRITTEN-20261005.md
  - plan-tournage-short-sandrina-15oct/
---

# Collège agentique — synthèse arbitrale

## Rôles et moteurs (traçabilité)
| # | Rôle | Moteur |
|---|------|--------|
| 1 | Planificateur production RS | qwen3.7-max |
| 2 | Community manager | mimo-v2.6-pro |
| 3 | Directeur marketing | grok-4.3 |
| 4 | UX / charge cognitive (TDAH) | mimo-v2.6-pro |
| 5 | Architecte systèmes autonomes | qwen3.7-max |
| 6 | Contradicteur (red team) | o4-mini |
| 7 | Briseur (rupture) | o4-mini |

> Réserve méthodo : contradicteur et briseur ont dû basculer sur le même moteur (o4-mini) après des 503 CometAPI (kimi, hunyuan-t1, llama-4-maverick indisponibles) — la diversité de moteurs est de 5 sur 7, pas 7 sur 7.

## Convergences (ce que le collège valide)
1. **Déclencheur = polling, pas webhook.** kDrive (WebDAV) ne pousse aucun événement. Cron `rclone` cost-zéro toutes les 10-15 min sur le dossier de dépôt. Cité par 6 rôles sur 7.
2. **Le système pousse, il n'attend pas** (ta règle). Notification + pastille d'état, jamais une app à ouvrir.
3. **Ne PAS construire de nouvel outil.** Industrialiser la page locale déjà existante (`semaine-41-travail/server.py + index.html + app.js`) au lieu d'ajouter Buffer/Notion/Postiz.
4. **Sandrina signe, la machine structure.** Le texte publié et l'accroche retenue ne sont jamais écrits par l'IA ; le score JEV est une aide, pas un décideur.
5. **`default_assignee` vide = panne silencieuse.** Toute carte kanban doit être assignée nommément, sinon elle disparaît de ta vue.
6. **Pérenniser les fragments hebdo** (`etat.yaml`, `journal.jsonl`, `LISEZ-MOI`) en une mémoire transverse — sinon on republie les mêmes accroches sans le savoir.
7. **Détecteur de panne par étage** (ta règle). Sans lui, la chaîne est muette.

## Désaccords — tranchés par l'arbitre
| Tension | Camps | Verdict |
|---|---|---|
| **Async (machine) vs Sync (atelier 3h/sem)** | Briseur vs 6 autres | **Refus de la rupture** (contredit ta demande explicite d'automatisation), **mais on garde la part juste** : un point de synchro fixe ≤60 min/semaine avec Sandrina = le « calendrier » humain le moins cher. |
| **Polling suffit-il, ou faut-il un stockage « push-capable » ?** | Contradicteur (sine qua non = event trigger) vs Architecte/Planificateur (polling OK) | **Polling suffit** (il ne t'attend pas, il tourne). MAIS le détecteur doit distinguer « vide car rien déposé » de « vide car token WebDAV expiré » — c'est là qu'est l'échec silencieux. Pas de changement de stockage. |
| **Cadence 2-4/sem vs 6/sem** | Planificateur vs Marketing | **Plafond 3/semaine, plancher 2.** Tu es opérateur unique (tournage + montage Filmora) : 6 suppose une délégation qui n'existe pas. |
| **Métrique pilote : complétion vs engagement** | Marketing vs CM | **Deux niveaux.** Indicateur avancé **automatisé** (taux de cases cochées) pilote le calendrier ; indicateur arrière **manuel** (saves/partages/DM, 5-8 min/sem) mesure l'audience. Ne pas confondre. |

## Zones d'ombre (angles morts — non vus par le collège)
1. **La « page locale » est fausse pour toi.** Les rôles raisonnaient « localhost ». Toi tu es sur Windows, le serveur est sur le VPS → la façade doit être servie sur le VPS en **URL publique** (`0.0.0.0:<port>`), pas en localhost. Sinon tu ne la vois pas.
2. **Le canal d'entrée réel de Sandrina n'est pas confirmé.** Le poll suppose un dossier kDrive ; on n'a pas vérifié QUEL dossier elle utilise (mail ? WhatsApp vocal ? dossier précis ?). À confirmer avant de câbler, sinon le poll surveille un dossier vide.
3. **Le coût caché reproduit ce que tu fuis.** Le contradicteur chiffre **5-10 h/semaine** de maintenance (workflows n8n + surveillance docker + scripts). Tu remplacerais « dépendre de Buffer » par « maintenir n8n ». C'est le risque n°1 de mort à 3 mois (**35 % de survie** estimés par le contradicteur).
4. **La boucle de mesure n'a pas de source automatique.** Aucune API analytics n'est branchée (clés présentes : Buffer/Postiz/Canva/Mistral — pas d'analytics). Ta règle « la mesure doit revenir vers moi » n'est donc PAS satisfaite : le maillon faible du dispositif.
5. **Le scope des 5 sorties n'a jamais été challengé.** « Mettre à jour les algorithmes des plateformes » est une **veille récurrente**, pas un livrable de production — à sortir du MVP.
6. **L'état « pas d'entrée » n'est pas géré.** Si Sandrina est en retard, rien n'est prévu (le contradicteur le note : dépendance Sandrina = point unique de défaillance).

## Test de non-évidence
Passé : aucune de ces recommandations n'est générique — elles s'appuient sur TES artefacts (`etat.yaml`, plan de tournage à cases, `LISEZ-MOI` de production, ligne édito JEV). Un consultant sans ces documents aurait proposé un SaaS de plus.

## MVP recommandé (un seul chantier, 1 semaine)
**La boucle « dépôt → page qui pousse »**, pas l'usine complète :
1. Poll `rclone` kDrive (10-15 min) sur le dossier réel de Sandrina → détection.
2. **Une seule sortie automatisée** : le plan de tournage (déjà existant, à cases) généré depuis la ligne édito.
3. Façade = ta page locale industrialisée, **servie par le VPS sur URL publique**, bandeau haut = jauge semaine + pastille de panne ; liste du jour = checklist binaire issue de `etat.yaml`.
4. Persistance : `git init` sur `sandrina-strategie/` → les fragments ne meurent plus.
5. Détecteurs (3 seuils) : dépôt non vu > 4 h ouvrées · token WebDAV suspect (dossier vide anormal) · page/serveur down.

**Contre-indication** : ne PAS câbler Postiz, Canva, ni les 4 autres sorties avant d'avoir bouclé UNE semaine complète avec ce MVP.

## Prochaine étape (dès validation)
Confirmer le canal d'entrée réel de Sandrina, puis monter la boucle. **Rien n'est exécuté.**
