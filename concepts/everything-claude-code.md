---
type: Concept
id: a70febd575e6
title: Everything Claude Code — analyse et adaptations Vagus
timestamp: 2026-08-23T22:30:00+02:00
tags:
  - reference-externe
  - claude-code
  - skills
  - securite
  - standards-code
related:
  - concepts/agent-plugin-standard.md
  - rules/session-hygiene.md
status: actif
---

# Everything Claude Code (WorldFlowAI) — analyse du 23/08/2026

Dépôt `WorldFlowAI/everything-claude-code` (1619 ⭐, ex-Affaan Mustafa, gagnant hackathon Anthropic).
Plugin Claude Code complet : 9 agents, 14 skills, 15 commands, 8 rules, 5 hooks.
**Repo figé depuis janvier 2026, licence MIT annoncée mais aucun fichier LICENSE.**

## Verdict de la confrontation avec la stack Vagus

1. **Doublons (rejet)** : hooks mémoire fichiers plats (nous : SQLite+FTS5+RAG), strategic-compact (nous : session-overflow-protocol), tmux hooks (nous : process management), optimisation modèles (déjà notre doctrine).
2. **Complémentaires (adaptés)** : continuous-learning → config paramétrable dans `session-maintenance` ; eval-harness EDD → pattern capability/regression (notre theme-verificateur en est déjà un cas métier).
3. **Gaps comblés (4 actions exécutées)** :
   - `audit-securite-repository` §9 : checklist rapide pré-commit (10 points + greps secrets/exfil)
   - `coding-standards-vagus` (nouveau) : standards transverses TDD/immuabilité/hygiène pour Vagus Quant, kleia-up, blackboard-engine, omp-rx, LangExtract
   - `session-maintenance` : section apprentissage continu paramétrable (seuils + ignore_patterns)
   - `vagus-context-guardian` Règle 11 : journal de compactions (~/hermes-cortex/logs/compaction-log.md) pour auditer les pertes de contexte

## Leçons

- Notre stack mémoire/continuité est **en avance** sur ce dépôt (le plus populaire du genre).
- Les gaps réels étaient : standards de code partagés, checklist sécurité rapide, traçabilité des compactions.
- Ne pas installer ce repo tel quel ; l'utiliser comme inventaire d'idées d'hygiène agentique.
