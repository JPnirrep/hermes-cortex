---
type: Concept
id: 50ea24592058
title: Plaquette KLEIA-UP V9 (finale)
description: Plaquette 16:9 landscape — 8 slides, version mutuelles, toutes corrections Sandrina intégrées
tags: [kleia-up, plaquette, marketing, design, mutuelles]
timestamp: 2026-07-17
owner: Sandrina
links: [kleia-landing-pages, vagus-kg-v2.1.md, lessons-session-20260715.md]
---

# Plaquette KLEIA-UP V9

**Format :** 16:9 landscape (1120×630px)
**Design system :** burgundy/gold/cream, Swiss Design + Muji minimal
**Host :** Python HTTP server 8080 → `http://135.125.53.215:8080/plaquette-mutuelles-v9.html`
**Fichier :** `site-web-kleia-up/plaquette-mutuelles-v9.html`

## Slides

| Slide | Titre | Spécificités V9 |
|-------|-------|-----------------|
| 01/08 | Cover | Photo 55% mask CSS, logo HD 96px, tagline « Leadership & Parole incarnée », bottom bar « Mutuelles et Entreprises à mission », signature Sandrina |
| 02/08 | Mouvement | Bio + badges + logos partenaires + témoignage UDAMS 85 + photo atelier |
| 03/08 | KPI | **Nouveaux :** 2 graphiques SVG (prise de conscience massive 65→90%, signal d'alarme 3,2→4,3%) + psy-inverse allégé |
| 04/08 | Respiration | Photo pleine page + overlay burgundy + citation dorée. **27/07 :** photo remplacée (scène_st_jean_1.png, bras ouverts), object-position 12% |
| 05/08 | CV | **Corrigé :** sous-titre + « hypersensibilité, lâcher prise », France Bleue, animatrice ateliers, forces de caractères, banner « Une approche qui fait la différence », clients mis à jour (Harmonie Mutuelle, La Poste, CPAM Mayenne) |
| 06/08 | Offres | **Corrigé :** textes reformulés, plus d'« optimisme stratégique », visio ajouté. **27/07 :** carte Conférence → Conférence Signature, titre « Cultiver l'optimisme : 3 clés pour soi et pour le collectif », nouvelle description |
| 07/08 | Pour qui | **Corrigé :** points finaux ajoutés aux bénéfices, barres colorées gold/blue/green/orange |
| 08/08 | Contact | CTA « Réservez votre échange offert », ref: Harmonie Mutuelle, « Imaginons ensemble » en or |

## Corrections Sandrina appliquées (17 juillet 2026)

Source : audio WhatsApp retranscrit.

### Bloc A — Slide 3
- **Graphiques SVG** : 2 charts inline (burgundy/gold), 3 barres chacun
- **Psy-inverse allégé** : « Cultivez ce qui va bien. L'engagement, la cohésion, la joie — vos meilleurs indicateurs de performance. »

### Bloc B — Slide 5 (CV)
- Sous-titre : ajouté « Hypersensibilité, lâcher prise — être soi »
- France Bleu : « Chroniqueuse 6 émissions » → « Interventions France Bleue »
- QVCT → « Animatrice d'ateliers collectifs »
- Forces VIA → intégré dans la ligne coach comme « forces de caractères »
- Banner : titre → « Une approche qui fait la différence », layout 2×2 grid, plus de « pas de PowerPoint »
- Clients ajoutés : Harmonie Mutuelle (Groupe VYV), La Poste, CPAM Mayenne, Maison et Services
- Témoignages : gardé Cécile Neuville, remplacé les 2 autres par des faits d'intervention

### Bloc C — Slide 6 (Offres)
- Intro : « Conférence pour ouvrir les perspectives. Atelier pour expérimenter. Formation pour ancrer durablement les pratiques. »
- Conférence : « forces de caractère, psychologie positive appliquée. Disponible en visio. »
- Formation : plus d'« optimisme stratégique », remplacé par coopération/engagement/responsabilité

### Bloc D — Slides 7-8
- Points finaux aux bénéfices
- Ref client : Harmonie Mutuelle (Groupe VYV)
- « Imaginons ensemble » → color:var(--gold)

## Corrections demandées mais pas de photo dispo
- Sandrina voulait changer photos cover et slide 2 → JP a confirmé photos OK

## CSS notable
- `.chart-row` / `.chart-card` / `.chart-svg` / `.chart-label` : SVG inline bars
- `.banner-grid` / `.banner-item` : grille 2×2 burgundy/gold pour le banner CV
- `.cible-bar` : barres colorées (gold/blue/green/orange) pour cibles

## Print CSS
- `@page { size: A4 landscape; margin: 0; }`
- Photos : `object-position` calculé pour portraits

## Serveur
- `cd /home/debian/workspace/site-web-kleia-up && python3 -m http.server 8080`
- Preview : `http://135.125.53.215:8080/plaquette-mutuelles-v9.html`
