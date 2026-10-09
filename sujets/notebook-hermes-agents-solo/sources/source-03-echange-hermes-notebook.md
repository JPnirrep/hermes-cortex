---
type: source
id: src-notebook-03
sujet: notebook-hermes-agents-solo
format: echange-webui
date: 2026-10-09
session: a34c4c4eccae
origine: conversation Hermes WebUI
---

# Source 03 — Échange du 09/10/2026 : Hermes peut-il faire comme NotebookLM ?

## Question initiale (JP)

> Je donne une source — peu importe un PDF, un document, un Excel, un PowerPoint, une
> image, un audio ou une vidéo — et Hermes le garde en ressources, le traite, le met dans
> un contexte sur un sujet donné. Il fait des transcriptions, il réfléchit sur comment
> exploiter cette ressource et la synthétise. Mais quand je travaille dans Hermes, je ne
> vois pas de manière synthétique et globale les sujets que je travaille ou que j'ai
> travaillés. Cela engendre des doublons et un manque de profondeur. Y a-t-il un moyen
> de faire ça d'une manière différente, sans quitter Hermes Web UI ?

## Réponse : OUI — avec une couche `sujets/`

### État mesuré (audit du 09/10/26)

| Élément | État réel |
|---|---|
| Ingestion PDF/DOCX/OCR/audio/vidéo/YouTube | OK — skills `ocr-and-documents`, `audio-transcription-cr`, `video-ocr-extraction`, `youtube-transcription` |
| RAG | opérationnel, 136 entrées, test score 0,63 sur « vue globale des sujets » |
| Périmètre indexé | concepts (43), rules (11), decisions (4), personas (3) — PAS reports/, research/, etudes-de-cas/ |
| `projects/` (10 dossiers) | VIDES, créés 10/07, jamais remplis, non indexés |
| Vue globale des sujets | AUCUNE — log.md est un journal chronologique, pas une carte |

### Cause racine

La connaissance est rangée par **atome** (concepts/) et par **chronologie** (log.md),
jamais par **sujet avec une synthèse vivante**. Rien ne dit « où on en est sur le sujet
X : ce qui a été fait, tranché, ce qui reste ouvert ». D'où doublons + manque de profondeur.

### Décision : couche `sujets/` = notebook, en mieux

1. Un dossier par sujet : `hermes-cortex/sujets/<slug>/` avec `index.md` (statut,
   registre des sources, synthèse vivante, questions ouvertes, décisions liées) et
   `sources/` (un `.md` par source : type, origine, sha256, extracteur).
2. **Aucun contenu original dupliqué** : le sujet indexe et synthétise, le fond reste
   dans `concepts/` et `workspace/`.
3. Anti-doublon à l'entrée : requête RAG avant toute création de sujet
   (`sujets.py check "<titre>"`) → si score élevé, rattacher à l'existant.
4. Vue globale générée automatiquement : `sujets.py dashboard` → `DASHBOARD.md`
   (statut, dernière activité, nb sources, questions ouvertes, alerte stale > 30 j).
5. Ajout de `sujets/` au périmètre du RAG et du watcher (indexation temps réel).
6. Garde-fous : plafond 10-25 sujets, règle de fusion, revue hebdomadaire.

### Contrepoints ARGOS

- Risque 3ᵉ étage de notes → neutralisé : le sujet ne contient aucun contenu original.
- Risque prolifération de sujets → plafond + détecteur de similarité + fusion.
- Risque synthèse périmée → `updated_at` + date de revue + alerte stale au dashboard.
- Écart NotebookLM irréductible : l'audio-overview automatique (compensable en TTS,
  non prioritaire). À l'inverse NotebookLM n'agit pas et n'a aucune vue inter-notebooks.

### Validation

JP valide la mise en œuvre immédiate avec cet échange comme première source
du premier sujet.
