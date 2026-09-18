---
type: Index
title: Hermes Cortex Central --- Bundle de Connaissance
description: Point d entree du bundle de connaissance Hermes.
owner: vagus
updated_at: 2026-07-10
version: 1.0
---

# Hermes Cortex Central

Bundle OKF du systeme Hermes / Vagus OS. Connaissance portable, typee, reliee.

## Regles fondamentales
- [Laicite absolue](rules/laicite.md)
- [Communication token-lean](rules/communication.md)
- [Design Language](rules/design-language.md)
- [Workflow JP](rules/jp-workflow.md)
- [Citations exactes](rules/citations-exactes.md)
- [Deny-Rules (policy fail-closed)](rules/deny-rules.yaml) — gate évalué avant chaque action, script `scripts/deny-check.py`

## Identifiants stables (ids)
Chaque note (concepts, rules, decisions, personas, patterns, playbooks) porte un
`id:` unique dans son frontmatter (uuid12, ex: `2f98ddbcbf66`). L'id est
l'identité stable de la note : **les références machine (RAG, KG, liens croisés)
doivent pointer par id, jamais par chemin** — un rename ne casse plus rien
(pattern Baalda « key by doc_id, never by path »). Le RAG retourne `source_id`
dans ses résultats. Ajout d'id manquant : `rag-env/add_ids.py` (idempotent).

## Index RAG temps réel
Le RAG est réindexé automatiquement dès qu'un fichier de connaissance change :
- **Watcher** : `rag-env/watch_cortex.sh` (inotify, service systemd user
  `cortex-watcher`) surveille concepts/rules/decisions/personas/patterns/playbooks
  → debounce 6 s → réindex incrémental. Create/update/delete couverts (prune).
- **Fallback** : cron `0 5 * * *` (sécurité réseau).
- **Anti-boucle** : rag_index.py n'écrit que `rag-index.db` (hors dossiers
  surveillés) + verrou flock anti-concurrence (`.index.lock`).
- L'index est un artefact **dérivé** : supprimable et reconstruisible à tout
  moment (`rm rag-index.db && python3 rag-env/rag_index.py`).

## Concepts metier
- [Custos Pricing](concepts/custos-pricing.md)
- [Custos Doctrine](concepts/custos-doctrine.md)
- [Custos Style Auteur](concepts/custos-style-auteur.md)
- [AT × CUSTOS](concepts/at-custos.md) — couche laïque d'interprétation (22 valeurs → comportements AT)
- [Agent Plugins Standard](concepts/agent-plugin-standard.md)
- [Protocole de collaboration JP-Hermes](concepts/protocole-collaboration.md) — le cycle en 6 temps de notre travail commun
- [Sandrina Livre HSP](concepts/sandrina-livre-hsp.md)
- [Custos Livre](concepts/custos-livre-age-transmettre.md)
- [Telegram Bot](concepts/telegram-bot.md)
- [Windows Reverse SSH](concepts/windows-ssh-tunnel.md)
- [Mode Browser Use (CLI 3.0)](concepts/browser-use-mode.md) — règles d'usage browser_exec + matrice VPS/local

## Projets actifs
- [CUSTOS](projects/custos/)
- [KLEIA-UP](projects/kleia-up/)
- [LOF](projects/lof/)
- [BrightBean](projects/brightbean/)
- [Framedeck](projects/framedeck/)

## Navigation rapide
- [Decisions](decisions/)
- [Playbooks](playbooks/)
- [Patterns](patterns/)
- [Critiques](critiques/)
- [References](references/)
- [Persona JP](personas/jp.md) — modele de fonctionnement de l'utilisateur (Sepharial + usage reel)

## Vault Obsidian
- Master index: /home/debian/workspace/hermes-vault/00-master-index.md
- Correspondance: vault-links.yaml
