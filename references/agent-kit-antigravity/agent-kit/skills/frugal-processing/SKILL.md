---
name: Frugal Processing
description: Optimisation de la consommation de tokens par réduction sémantique (shaving) avant envoi au LLM.
---

# ✂️ Skill de Token-Shaving

Ce module applique les principes de frugalité du système Antigravity pour réduire les coûts opérationnels de 15 à 20%.

## 1. Algorithmes de Shaving
- **Denoising** : Suppression des balises HTML inutiles, des espaces multiples et des commentaires de code non pertinents.
*   **Semantic Compression** : Remplacement des formulations verbeuses par des équivalents concis.
*   **Stop-word Cleaning** : (Optionnel) Retrait des mots de liaison à faible valeur ajoutée dans les contextes de recherche.

## 2. Usage
```python
python .agent/skills/frugal-processing/scripts/shave.py --input <file>
```
