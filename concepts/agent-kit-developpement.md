---
type: concept
id: c4b49ae4184c
title: Kit agent de développement (ex-antigravity)
version: 1.0.0
owner: JP / Vagus OS
created: 2026-10-20
timestamp: 2026-10-20
tags: [dev, opencode, cursor, codex, agent, reference, fusion]
sources:
  - antigravity-brain/.agent (fusion, gelé 18/05/2026)
links:
  - skills:omp-cli-orchestration
  - skills:coding-standards-vagus
  - skills:audit-application-source
  - concepts/kleia-brand.md
---

# Kit agent de développement (ex-antigravity)

**Objet : framework d'ingénierie logicielle générique** récupéré de l'ancien antigravity-brain.
Référence réutilisable pour OMP et les workflows de dev Vagus — **pas** du contenu métier Kleia.

## Localisation

`references/agent-kit-antigravity/agent-kit/` (~5,2 Mo)

## Composition

| Sous-dossier | Contenu | Usage |
|---|---|---|
| `.opencode/commands/` | 34 commands (plan, tdd, review, security, quality-gate, refactor…) | prompts slash pour agent opencode |
| `.opencode/prompts/agents/` | 14 prompts d'agents (architect, code-reviewer, database…) | rôles spécialisés |
| `.cursor/rules/` + `.cursor/skills/` | 39 règles + 11 skills (coding-style multi-langages) | standards de code |
| `.codex/`, `.claude-plugin/`, `.shared/` | config agents Codex / Claude | glue éditeurs |
| `agents/`, `workflows/`, `skills/`, `rules/`, `scripts/` | framework générique (backend/frontend/db/devops…) | bibliothèque de capacités |

## Règles d'usage

- **Filtre d'interdit appliqué** : les 14 fichiers référençant Mercury, Gemini, MiroFish ou
  trading swarm ont été **purgés** (fournisseurs interdits depuis 04/09/2026). Ne jamais les réintroduire.
- **Référence, pas duplication** : piocher une commande/règle au besoin et l'adapter dans le skill
  Hermes ou la commande OMP cible, plutôt que de copier le kit en bloc.
- **Obsolescence partielle** : le kit date d'avril–mai 2026 ; toujours recouper avec
  `skills:coding-standards-vagus` (TDD, immutabilité, zéro debug) avant d'en adopter une règle.
