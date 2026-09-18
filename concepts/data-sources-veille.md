---
type: Concept
id: c4cae11c20f7
title: Sources de données — veille et sourçage
timestamp: 2026-08-21
tags: [data, sources, veille, datasets, statistiques, recherche]
links: [rules/multi-sources-research.md, concepts/custos-doctrine.md, concepts/browser-use-mode.md]
---

# Sources de données identifiées (Beyond Google, 21/08/26)

Les 9 sites de la vidéo « Data Science Websites Most People Don't Know Exist »
(Beyond Google, wlE9kEqwsF8), vérifiés en ligne le 21/08/26 (HTTP 200),
mappés aux usages Vagus OS.

## Datasets

- **Google Dataset Search** — datasetsearch.research.google.com — moteur de
  datasets (Kaggle, GitHub, portails publics). Usage : sourçage scientifique —
  psychologie positive (Fredrickson), hypersensibilité (Aron), santé mentale au
  travail → plaquette mutuelles, contenus Sandrina.
- **Data Is Plural** — data-is-plural.com — newsletter hebdo de datasets
  insolites, CSV prêt à l'emploi. Usage : matière première veille/newsletters
  LOF + KLEIA-UP.
- **UCI ML Repository** — archive.ics.uci.edu — datasets ML classiques.
  Usage : Vagus Quant (marginal ailleurs).

## Comprendre les concepts (pédagogie)

- **Seeing Theory** — seeing-theory.brown.edu — probabilités & stats
  interactives (Brown University).
- **Setosa.io** — explications interactives stats/ML.
- **Distill** — distill.pub — articles ML expliqués en visuel (journal
  archivé, contenu toujours en ligne).
- **R2D3** — r2d3.us — intro visuelle ML, basique (décoratif).

Usage : KLEIA-UP, vulgarisation, contenus pédagogiques.

## Apprendre / pratiquer

- **OpenIntro** — openintro.org — manuels de stats gratuits + exercices.
  Usage : vérifier les notions (corrélation ≠ causalité, tailles d'effet)
  avant de publier un chiffre. Anti-bêtise éditoriale.
- **Tableau Public** — public.tableau.com — galerie de dashboards réels.
  Usage : inspiration dataviz pour rapports et infographies.

## Verdict usage (21/08/26)

- Priorité haute : **Dataset Search** + **Data Is Plural**.
- Priorité moyenne : OpenIntro + Tableau Public.
- Ponctuel : Seeing Theory / Setosa / Distill.
- Marginal : UCI (hors Vagus Quant), R2D3.

## Notes techniques

- Captions YouTube bloquées par IP cloud (bot-wall) — contenu confirmé via la
  description complète extraite du DOM (`attributedDescription`), pas de site
  manquant.
- SSL Python cassé par `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` pointant vers
  /home/debian/.hermes/*.pem → `unset` avant toute requête Python externe.
- Liens : [Mode Browser Use](browser-use-mode.md) pour les blocages anti-bot.
