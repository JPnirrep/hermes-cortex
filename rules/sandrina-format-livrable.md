---
type: Leçon
id: sandrina-format-livrable
title: Format attendu des livrables Sandrina — un post = un dossier daté
tags: [sandrina, livrable, format, lisibilite, lecon]
timestamp: 2026-10-02
links: [sandrina-ligne-editoriale-20261005.md, sandrina-visuels-banque.md]
---

# Leçon — le format, pas seulement le fond

**Retour JP (02/10/2026)** : « tu as ajouté du travail dans la ligne édito de sandrina, ça ne va pas
avec son organisation. la mise en forme est illisible pour sandrina. il faut mieux structurer et
simplifier pour lui montrer l'essentiel important pour elle. »

## Le diagnostic

Le livrable `PLAN-SEMAINE-5-9-OCTOBRE.md` (284 lignes) parlait **du** travail de Sandrina :
scoring JEV, tableaux d'analyse, « les 3 décisions qui restent », métadonnées, justifications.
C'est un **rapport de conseil**, pas un **outil de travail**.

Son document d'origine (`Ligne_éditoriale_semaine_du_5_au_9_octobre.docx`) est un fichier
**par jour** : son texte + ses conseils techniques de tournage. Rien d'autre.

## Son organisation réelle (à respecter)

`/home/debian/.hermes/profiles/sandrina/work/`

| Zone | Contenu |
|---|---|
| `01-ecriture/` | textes du livre, accords, récits |
| `02-visibilite/` | posts LI/IG/YT, légendes, scripts |
| `03-strategie/` | positionnement, offres, cap |
| `04-retours/` | retours bêta-lectrices, avis |
| `10-templates/` | 4 gabarits : post-linkedin, post-instagram, post-youtube, fiche-validation |

Convention : **un post = un dossier daté** dans `02-visibilite/` (ex. `2026-09-30-post-coulisses/`).

## La règle (anti-récurrence)

1. **Livrable Sandrina = son document à elle, en clair.** Jamais un rapport sur elle.
2. **Un fichier par jour**, dans `02-visibilite/AAAA-MM-JJ_semaine/`.
3. **Elle ouvre, elle lit, elle copie.** Aucune ligne à rédiger de son côté.
4. **Le texte intégral est dans le corps du fichier**, pas un résumé ni un lien.
5. **Les visuels sont codés 🟢 déjà là / 🟡 à faire / 🔴 à écarter**, avec l'emplacement kDrive exact.
5b. **Anonymisation volontaire des participantes** (décision JP, 02/10/2026) : les 6 femmes coachées
   ne sont **pas nommées** — « 6 femmes exceptionnelles ». Ne pas les nommer, ne pas réclamer
   leurs prénoms, ne pas laisser dans son document de case à remplir qu'elle ne peut pas remplir.
6. **Le raisonnement (scores, analyses, arbitrages) reste hors de son document** : il va chez JP
   ou dans `03-strategie/`, jamais dans la ligne édito.
7. **La page d'accueil tient en un écran** : un tableau jour → fichier, le lien, ce qui reste à décider.

## Contre-exemple conservé

`PLAN-SEMAINE-5-9-OCTOBRE.md` — utile pour JP (vue d'ensemble, arbitrages), **inadapté à Sandrina**.
Ne pas le lui envoyer.

## Livrable conforme (référence)

`~/.hermes/profiles/sandrina/work/02-visibilite/2026-10-05_semaine/`
= `LIRE-MOI.md` + `mardi-06.md` + `mercredi-07.md` + `jeudi-08.md` + `vendredi-09.md`
(+ export `SEMAINE-5-9-OCTOBRE-Sandrina.{odt,docx}` dans `workspace/sandrina-strategie/export/`).
