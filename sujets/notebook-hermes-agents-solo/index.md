---
type: sujet
id: nbk-a93f2c7d51e4
titre: Notebook Hermes — organisation des sources et des agents pour solo
slug: notebook-hermes-agents-solo
statut: actif
created_at: 2026-10-09
updated_at: 2026-10-09
next_review: 2026-11-08
tags: [notebook, hermes, architecture, agents, solo, ingestion, sources, vue-globale, anti-doublon]
nb_sources: 3
nb_questions_ouvertes: 0
links:
  - concepts/protocole-collaboration.md
  - concepts/data-sources-veille.md
  - rules/jp-workflow.md
---

# Notebook Hermes — organisation des sources et des agents pour solo

## Synthèse vivante

### v1 — 2026-10-09 (source 01 + 02 + 03)

**Le besoin.** JP veut déposer n'importe quelle source (PDF, Excel, PPTX, image, audio,
vidéo) dans Hermes, qu'elle soit transcrite, rattachée à un sujet, synthétisée — et
surtout voir **globalement** quels sujets il travaille, pour éviter doublons et travail
superficiel. Contrainte : tout reste dans Hermes Web UI, sans nouvel outil externe.

**Le constat (mesuré).** La chaîne d'ingestion existe déjà et dépasse NotebookLM
(extraction, OCR, transcription, TTS). Ce qui manque n'est pas technique : c'est le
**rangement par sujet**. Rangé par atome (43 concepts) et par date (log.md), l'état
d'avancement d'un thème n'existe nulle part ; `projects/` est un squelette vide (10
dossiers, 0 .md).

**La décision.** Couche `sujets/` : un dossier par sujet avec `index.md` (synthèse
vivante versionnée + registre des sources + questions ouvertes) et `sources/` (une fiche
par source, sha256 + extracteur). Un dashboard généré (`DASHBOARD.md`) donne la carte
globale, régénéré à chaque changement. Anti-doublon : requête RAG obligatoire avant de
créer un sujet.

**Apport des agents (source 01).** Pour un solo, le goulot n'est pas la compétence mais
l'énergie et le temps de cerveau. Les agents spécialisés en arrière-plan jouent un comité
de direction virtuel sur 5 pôles : créer/structurer, communiquer/rédiger,
vendre/prospecter, tourner/produire, et surtout le couplage + mémoire (zéro perte de
contexte, travail en réseau entre agents).

**Application KLEIA-UP (source 02).** 2 à 3 bots suffisent : « Stratégie & Éditorial »
(mémoire du positionnement, déclinaison des notes vocales en posts/newsletter/argumentaires)
et « Opérations & Logistique » (structure des ateliers, livrets pédagogiques, cohérence
des parcours), coordonnés sur un canal partagé. Gain annoncé : 80 % du travail de
rédaction, structuration et suivi pré-attrapé pendant que Sandrina préste.

**Ce que ça change.** Le sujet devient l'unité de navigation : on retrouve le thème par
titre (« Notebook… »), on part de la synthèse vers les sources, et le dashboard remplace
les fouilles dans log.md.

## Registre des sources

| # | Source | Format | Date | Fichier |
|---|--------|--------|------|---------|
| 01 | Intérêts des agents spécialisés pour un solo | PDF (77 742 o, texte natif) | 2026-10-09 | [sources/source-01-interets-agents-solo.md](sources/source-01-interets-agents-solo.md) |
| 02 | Exemple KLEIA-UP / Sandrina Perrin — 2-3 bots | PDF (79 053 o, texte natif) | 2026-10-09 | [sources/source-02-exemple-kleia-up.md](sources/source-02-exemple-kleia-up.md) |
| 03 | Échange WebUI — Hermes comme NotebookLM (besoin, audit, décision) | Conversation | 2026-10-09 | [sources/source-03-echange-hermes-notebook.md](sources/source-03-echange-hermes-notebook.md) |

## Sessions liées

| Date | Session | Apport |
|---|---|---|
| 2026-10-09 | `a34c4c4eccae` | Echange fondateur: besoin NotebookLM, audit etat, creation couche sujets |

## Questions ouvertes

- [x] Plafond de sujets : **15** (décision JP, 09/10/26) — au-delà, fusion obligatoire, crée un nouveau sujet par manifestation de dispersion plutôt que de dédupliquer.
- [x] Seuil anti-doublon calibré à **0,70** (décision JP, 09/10/26) : doublon évident = 0,771 (alerté), sujet connexe ≈ 0,62 (passé) — coupe propre entre les deux.
- [x] RAG étendu à reports/, etudes-de-cas/, research/ (décision JP, 09/10/26 — 5 fichiers, 35 Ko : ces travaux étaient invisibles = doublons assurés).
- [x] Dashboard : régénéré au changement uniquement (décision JP, 09/10/26) — le watcher couvre déjà, un cron serait un coût récurrent pour rien. Détecteur de panne = date de génération affichée en tête.
- [x] Sources hors cortex : vault-links UNIQUEMENT quand la source est réutilisable (décision JP, 09/10/26) — pas de réindexation proactive de workspace/.

## Règles du sujet

- **Plafond : 15 sujets** — au-delà, on fusionne avant de créer (règle JP 09/10/26).
- **Seuil anti-doublon : 0,70** — score ≥ 0,70 sur un sujet existant = rattachement obligatoire, pas de création.

## Décisions liées

- 2026-10-09 : création de la couche `sujets/` + dashboard + anti-doublon (validation JP, source 03).
- 2026-10-09 : réglages JP — plafond **15 sujets**, seuil anti-doublon **0,70**.
- Voir aussi `concepts/protocole-collaboration.md` (cycle JP-Hermes) pour l'usage des synthèses.

## Liens

- [Protocole de collaboration JP-Hermes](../concepts/protocole-collaboration.md)
- [Data sources veille](../concepts/data-sources-veille.md)
- [Workflow JP](../rules/jp-workflow.md)
- [DASHBOARD](../DASHBOARD.md) — carte globale de tous les sujets
