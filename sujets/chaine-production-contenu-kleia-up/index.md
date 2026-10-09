---
type: sujet
id: nbk-28278e171bf1
titre: Chaîne de production de contenu Kleia-up / Sandrina — collège agentique + MVP
slug: chaine-production-contenu-kleia-up
statut: actif
created_at: 2026-10-09
updated_at: 2026-10-09
next_review: 2026-11-09
tags: [kleia-up, sandrina, production, contenu, n8n, kanban, college-agentique, kdrive, ux]
nb_sources: 10
nb_questions_ouvertes: 4
links:
  - concepts/sandrina-ligne-editoriale-20261005.md
  - concepts/sandrina-visuels-banque.md
  - sujets/tournage-short-sandrina-15oct/index.md
---

# Chaîne de production de contenu Kleia-up / Sandrina — collège agentique + MVP

## Synthèse vivante

### v1 — 2026-10-09 (session 19dbb0d40d1b)

**Objet.** Passer d'une production de contenu **manuelle, fragmentée, hebdomadaire et aveugle**
à une chaîne **durable, visible et qui POUSSE** vers JP, tout en gardant **Hermes comme cerveau**
et une façade facile (JP a rejeté Buffer et Notion : « pas faciles »).

**Constat d'ancrage (important).** La chaîne demandée **existe déjà en morceaux** produits à la main
dans `workspace/sandrina-strategie/` : `LIGNE-EDITO-REWRITTEN-20261005.md` (accroches scorées JEV),
`plan-tournage-short-sandrina-15oct/` (plan HTML+PDF **à cases à cocher**), `semaine-41-travail/`
(`etat.yaml` = état par jour, `donnees.yaml`, `journal.jsonl` = journal horodaté, `server.py` +
`index.html` + `app.js` = petit serveur **local**, `verifier.py`), `production/mercredi-07/`
(visuels + `LISEZ-MOI` = manifeste IDs kDrive / formats / facteurs d'agrandissement).
**Le problème n'est pas l'absence d'outil : c'est l'absence de continuité** — ces fragments meurent
en fin de semaine et aucune vue transverse n'existe.

**Collège agentique (7 rôles, 5 moteurs).** Délibération contradictoire ; contributions et arbitrage
dans `sources/`. Convergences : (1) le déclencheur **ne peut pas être un webhook** (kDrive n'en pousse
pas) → **poll rclone coût-zéro** ; (2) **ne pas construire d'outil neuf** — industrialiser la page
locale existante ; (3) **Sandrina signe, la machine structure** (jamais son texte publié par IA) ;
(4) pérenniser les fragments hebdo ; (5) `default_assignee` vide = panne silencieuse ; (6) détecteur
de panne **par étage**.

**Désaccords tranchés.** Briseur (abandonner le pipeline pour un atelier 3 h/sem) → **refusé**, mais
on garde un point de synchro ≤ 60 min/sem avec Sandrina. Contradicteur (il faut un stockage push) →
**polling suffit**, à condition de distinguer « rien déposé » de « token WebDAV expiré ». Cadence →
**plafond 3/sem, plancher 2** (JP seul à tourner + monter). Métrique → **deux niveaux** (avancé
automatisé = taux de cases cochées ; arrière manuel = saves/partages).

**Zones d'ombre (angles morts).** (a) la « page locale » est fausse pour JP (Windows ↔ VPS → l'URL
doit être **publique**, pas localhost) ; (b) **canal d'entrée réel de Sandrina non confirmé** ;
(c) coût caché **5-10 h/sem** de maintenance n8n (= reproduire ce qu'il fuit, survie 3 mois estimée
35 %) ; (d) boucle de mesure **sans source automatique** (aucune API analytics) ; (e) la 5ᵉ sortie
« mettre à jour les algos plateformes » = **veille**, pas un livrable → hors MVP.

**MVP recommandé (1 semaine, boucle d'abord).** Poll `rclone` kDrive (10-15 min) → **une seule sortie
automatisée** (plan de tournage depuis la ligne édito) → façade = page locale industrialisée **servie
par le VPS en URL publique** (jauge semaine + pastille de panne + checklist binaire issue de
`etat.yaml`) → `git` sur `sandrina-strategie/` (continuité) → 3 détecteurs (dépôt non vu > 4 h ·
token WebDAV suspect · page/serveur down).
**Contre-indication :** ne pas câbler Postiz / Canva / les 4 autres sorties avant une semaine complète.

**Statut : RIEN n'est exécuté** — en attente des 2 décisions JP (ci-dessous).

## Registre des sources

| # | Source | Fichier | Format |
|---|--------|---------|--------|
| 01 | Mémo vocal JP « gestion des créa » | `raw/01-memo-audio.m4a` | audio-m4a |
| 02 | Transcription du mémo | `raw/02-memo-transcription.txt` | txt |
| 10 | Collège — 7 contributions (1 planificateur, 2 CM, 3 marketing, 4 UX, 5 architecte, 6 contradicteur, 7 briseur) | `raw/10-college-*.md` | md |
| 20 | Synthèse arbitrale | `raw/20-synthese.md` | md |

## Sessions liées

| Date | Session | Apport |
|---|---|---|
| 2026-10-09 | `19dbb0d40d1b` | Mémo audio transcrit ; collège agentique 7 rôles/5 moteurs ; arbitrage ; MVP boucle dépôt→page ; angles morts. Rien exécuté. |

## Questions ouvertes

- [ ] **Par quel canal Sandrina dépose-t-elle réellement ?** (kDrive précis / mail / note vocale) — conditionne le poll.
- [ ] MVP « boucle d'abord » validé, ou architecture technique complète d'abord ?
- [ ] La façade doit-elle être servie par le VPS en URL publique (confirmé nécessaire) — quel port/domaine ?
- [ ] Sortir « mise à jour des algo plateformes » du MVP (traitée comme veille à part) ?

## Décisions

- D1 (2026-10-09, collège) : déclencheur = **poll rclone kDrive coût-zéro**, pas de webhook (impossible).
- D2 (2026-10-09, collège) : **ne pas bâtir d'outil neuf** — industrialiser la page locale existante.
- D3 (2026-10-09, collège) : **Sandrina signe**, la machine structure ; jamais son texte publié par IA.
- D4 (2026-10-09, collège) : cadence **2-3 contenus/semaine** (opérateur unique).
- D5 (2026-10-09, collège) : MVP = boucle **dépôt → page qui pousse** ; le reste plus tard.
