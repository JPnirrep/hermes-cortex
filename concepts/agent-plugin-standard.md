---
type: Concept
id: 94741770ef8d
title: Standard Agent Plugins — Livraison Client
timestamp: 2026-08-07
tags: [standard, packaging, agent-plugins, skills, mcp, clients, deploiement]
links: [rules/communication.md, concepts/custos-doctrine.md, rules/jp-workflow.md]
---

# Standard Agent Plugins — Livraison Client Vagus OS

## Décision

Vagus OS adopte **Agent Plugins 1.0.0** (agent-plugins.org) comme format standard
de packaging et de livraison des solutions agentiques aux clients. Spec ouverte,
vendor-neutral, TSC composé d'Amazon, Cursor, Microsoft, OpenAI, Vercel + Google
(2026-08). C'est le moment Docker du packaging agent : standardiser l'emballage
sans imposer de runtime.

## Pourquoi

- **Crédibilité** : livrer un format que VS Code, Cursor, GitHub Copilot,
  ChatGPT/Codex et Kiro chargent nativement (compatible-clients officiel).
- **Rapidité** : une seule structure à produire, valable partout. Le client
  n'invente plus sa boîte.
- **Robustesse** : échec indépendant des composants (un MCP qui plante ne tue
  pas les skills), schéma fermé, containment des chemins.

## La boîte (structure canonique)

```
client-kit/
├── plugin.json          # manifest REQUIS ($schema + name obligatoires)
├── skills/              # un sous-dossier par skill, SKILL.md à la racine
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
├── mcp.json             # optionnel, $schema + mcpServers (stdio|streamable-http|sse)
└── com.vagus.client/    # namespace extension reverse-domain (facultatif)
```

## Règles normatives (résumé exécutif)

| Domaine | Règle |
|---|---|
| plugin.json | Schéma FERMÉ : `$schema`, `name` requis. 10 champs max. Champ inconnu = report+ignore (non-fatal). Toute autre violation = plugin rejeté. |
| name | 1-64 chars, `a-z0-9.-`, pas de `--` ni `..`, début/fin alphanumérique. |
| skills/ | Découverte par emplacement FIXE. Pas de recherche récursive profonde. Skill invalide = skip, pas de rejet global. |
| SKILL.md | Spec Agent Skills (agentskills.io) : frontmatter `name` (== dossier), `description` (1-1024), `metadata` = map string→string, `license`, `compatibility`, `allowed-tools`. |
| mcp.json | `$schema` + `mcpServers`. Variants fermés : stdio (command token unique, pas de ligne shell), streamable-http, sse (legacy). |
| Chemins | Plugin-relative doit commencer par `./` et rester dans le root. `cwd` accepte `./`, `${PLUGIN_ROOT}/`, `${PLUGIN_DATA}/`. |
| Secrets | JAMAIS de credentials dans `headers` ou `env` (visible package data). Auth = côté client. |
| Placeholders | `${PLUGIN_ROOT}` et `${PLUGIN_DATA}` expansés dans args/env/cwd uniquement. `command` jamais interpolé. |
| Résilience | Un serveur qui échoue = skip + continue. Pas de fallback de transport automatique. |
| Versioning | `$schema` déclare la version cible. mcp.json doit matcher plugin.json. SemVer recommandé. |

## État de notre écosystème (audit 2026-08-07)

- **143 skills** Hermes : noms 100% valides, descriptions présentes.
- **~40 skills** ont des champs top-level hors spec (author, version, category,
  platforms, tags, triggers, conditions...) → l'exporteur les déplace sous
  `metadata:` avec préfixe `hermes:`.
- Structure Hermes = `skills/<categorie>/<skill>/SKILL.md` → l'export aplatit
  la catégorie (le validateur Agent Skills n'accepte que les enfants directs
  de `skills/`).

## Outillage (workspace/agent-plugin-standard/)

| Script | Rôle |
|---|---|
| `scaffold_new_plugin.py` | Génère un plugin client conforme (plugin.json + skill exemple + mcp.json optionnel). |
| `export_skill.py` | Exporte un skill Hermes → Agent Skills conforme (normalise frontmatter, sérialise metadata). |
| `validate_plugin.py` | Validateur spec 1.0.0 : plugin.json, mcp.json, skills, containment, extensions. `--strict` = warnings fatals. |

## Workflow livraison client

1. Scaffold : `scaffold_new_plugin.py <nom-client> --author "Vagus OS" --with-mcp`
2. Exports : `export_skill.py <skill-src> <plugin-dir>` pour chaque skill du périmètre
3. Config MCP : ajouter les serveurs dans mcp.json (stdio pour local, streamable-http pour SaaS)
4. Validation : `validate_plugin.py <plugin-dir> --strict` → **doit sortir CONFORME, exit 0**
5. Livraison : dossier zip ou git. Le client le dépose dans le dossier plugins de son client compatible.

## Risques / Limites (ARGOS)

- **Pas de canal de confiance** : pas de provenance ni signature en v1 → à
  surveiller pour livraisons sensibles (chiffrer le zip, canal direct).
- **`com.example.client/`** : échappatoire de fragmentation — ne pas en dépendre,
  rester dans le core portable.
- **Clients compatibles vérifiés** : VS Code, Cursor, GitHub Copilot,
  ChatGPT/Codex, Kiro. Vérifier la liste avant promesse client.
- Hermes lui-même ne charge pas encore le format Agent Plugins nativement
  (notre loader = skills/ + SKILL.md, sans plugin.json) — l'export est
  one-way vers les clients compatibles.

## Conformité Hermes → Agent Plugins

Notre structure est à ~90% du format sans le savoir. Le delta = `plugin.json`
(2 lignes), aplatissement des catégories, normalisation du frontmatter.
Coût d'ajout d'un plugin.json à un skill existant : ~10 minutes.
