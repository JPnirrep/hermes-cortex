---
type: concept
id: hermes-devis-generateur-20261023
title: Génération de devis (hermes-devis) — repro vérifiée
description: Générateur de devis A4 5 pages (JSON → HTML → PDF via Chromium), étudié depuis kDrive et reproduit à l'identique sur le VPS. Prêt pour les demandes Sandrina.
owner: Sandrina / JP
timestamp: 2026-10-23
tags: [devis, sandrina, kleia-up, pdf, generation, hermes-devis, playwright, chromium]
links: [kleia-brand.md, plaquette-kleia-up.md, infomaniak-kdrive, hermes-devis-production]
---

# Génération devis — hermes-devis

Source kDrive : `KLEIA-UP/KLEIA-UP/06_OPERATIONS_ET_TECHNIQUE/hermes-devis-1dca17ba/hermes-devis/`
Copie d'étude : `/tmp/hermes-devis-study/hermes-devis/`

- Principe : contenu séparé du rendu. On édite le JSON (ex. `examples/devis-2026-202.json`), jamais le PDF.
- Exécution : `node generate.mjs data.json output/devis.pdf` → PDF A4 + HTML autonome + rapport audit JSON.
- Prérequis : Node ≥20, npm, Chromium (playwright-core 1.64.1). Install Debian : `./install-debian.sh && npm run generate` (ou `CHROME_BIN=/usr/bin/google-chrome node generate.mjs ...`).
- Blocs : header, title, heading, paragraph, callout, quote, list, panel, table (journey/value), forfait, options, signatures, footer.
- Règles : A4 210×297, marges 20/20/18/18 mm, Noto Sans locale, accents terracotta, tableaux/panneaux jamais éclatés, pas d'orphelins de titre.
- Reproduit 23/10/26 : `npm ci` OK, `node tests.mjs` 5/5 OK, génération 5 pages OK, contrôle visuel pages 1 et 5 propre (aucun débordement).

Limites (ARGOS) :
- Le moteur ne calcule ni prix ni TVA ni CGV — chiffres et mentions légales à valider par Sandrina.
- Rendu reconstruit, pas pixel-perfect vs PDF approuvé (retours ligne/espacements peuvent différer légèrement).
- Un seul type de doc (devis) pour l'instant ; autres types (facture, contrat, lettre) nécessitent d'adapter les blocs.
