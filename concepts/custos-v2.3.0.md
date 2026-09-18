---
type: Concept
id: 5aa817ace00e
title: CUSTOS Moteur v2.3.0
description: Version corrigée du calculateur — 43/43 tests + 545 robustesse
tags: [custos, version, moteur, calculateur]
timestamp: 2026-07-13
owner: SNC Vagus OS
links: [custos-6-methodes.md, custos-doctrine.md, custos-v2.2.1.md]
---

# CUSTOS Moteur v2.3.0

## Corrections appliquées

| Correction | Problème | Solution |
|---|---|---|
| Millui Gimel | 53 au lieu de 83 | Lamed (30) ajouté → גימל complet |
| Aleph initial | Aucun א en début de mot E/I/O/U/Y | Ajout automatique (Olivier→אוליביה) |
| Lettre A | Systématiquement omis | A début/fin→א, milieu→omis |
| É final | Toujours י (René→רני) | É fin→ה (René→רנה) |
| Table exceptions | 25 noms bibliques mal transcrits | Formes hébraïques classiques + basculement auto |
| Accents tréma | Raphaël/Anaël non reconnus | Support des deux formes |

## Tests

- **Tests unitaires** : 43/43 PASS
- **Tests de robustesse** : 545 — 140+ prénoms français 2015-2025, 30 rares, 50+ internationaux, 12 composés, 8 cas bord
- **Zéro échec, zéro crash**

## CHANGELOG

Fichier : `/home/debian/workspace/custos/src/CHANGELOG.md`
Version : 2.3.0
