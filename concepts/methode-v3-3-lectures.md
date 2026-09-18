---
type: concept
title: Methode V3 3 Lectures CUSTOS
timestamp: 2026-08-29
id: b6fe6909aa29
---

type: concept
title: Methode V3 3 Lectures CUSTOS
tags: [custos, gematria, methode, v3, sandrina]
timestamp: 2026-07-23
links:
  - concepts/sandrina-livre-hsp.md
  - ../../custos/docs/calculs/methode-v3-3-lectures.md
---

## Méthode V3 des 3 lectures gematriques

Utilisée dans le thème Sandrina Perrin V3 (gold standard).
Non implémentée dans le calculateur.py actuel (v2.3.0).

### Calcul
1. **Vision** = standard total (prenom+nom) → base22
2. **Potentiel** = digit9(prenom_std) + digit9(nom_std)
3. **Expression** = digit9(prenom_atb) + digit9(nom_atb)

### Verdict
- Perrin (16/7/4) ✅ reproductible — intégré dans matrice_complete()
- Van-Reckem (17/8/8) ✅ reproductible — thème disait 18/9/21
- Delta CV (56.7%) ✅ implémenté — thème utilisait 12% narratif
- Analyse transgénérationnelle ✅ disponible via analyse_transgenerationnelle()

L'écart Van-Reckem (17/8/8 vs 18/9/21 du thème) et le delta
narratif 12% sont documentés dans custos/docs/calculs/v3-transgenerational.md

### Action recommandée
✅ RÉSOLU — Implémenté dans calculateur.py (v2.4.0+).
Fonctions : `trois_lectures_v3()`, `reduction_9()`, `coeff_variation()`,
`archetype_info()`, `analyse_transgenerationnelle()`.
Intégré dans `matrice_complete()` → clé `lectures_v3` dans le JSON de sortie.
