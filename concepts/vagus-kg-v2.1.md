---
type: Concept
id: 18507269582a
title: Vagus Knowledge Graph v2.1
description: Ontologie light consolidée — 45 nœuds, 47 relations, 6 clusters
tags: [vagus, kg, knowledge-graph, infra]
timestamp: 2026-07-13
owner: SNC Vagus OS
links: [kleia_knowledge_graph.yaml, plaquette-kleia-up.md]
---

# Vagus Knowledge Graph v2.1

Généré le 13 juillet 2026 via 3 subagents de cartographie parallèle.

## Contenu

| Type | Nœuds |
|---|---|
| Projets (11) | KLEIA_UP, LOF, CUSTOS, BRIGHTBEAN, Framedeck, site-web, vagus-quant, livre-hsp, youtube-corpus, transparence-citoyenne |
| Services (16) | hermes-gateway, headroom, prism, n8n, shared-postgres, caddy, agent-vault, vaultwarden, mcp-gateway, recursivemas, canva-mcp, kleia-bridge, telegram, whatsapp... |
| Providers (5) | DeepSeek, Gemini, OpenRouter, Inception, CometAPI |
| Personnes (3) | JPP, Sandrina, Hermes |
| Ressources (5) | kg-file, nucleus, manifesto, vagus-state, session-db |
| Infra (3) | vps-ovh, windows-jpp, docker-host |

## Relations

6 types : `depends_on`, `feeds_into`, `contains`, `blocks`, `manages`, `proxies`, `uses`, `competes_with`

## Fichier
`~/.hermes/context/kleia_knowledge_graph.yaml`

## Parser
`~/.hermes/context/kg_engine.py` — CLI + NL query

## Économie tokens
AVANT : MEMORY.md (3.2K) + index (0.2K) = ~3.4K tokens/session
APRÈS : `kg_engine.py status` = ~1.2K tokens → **-65%**
