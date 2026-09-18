---
type: regle
title: Manifeste de dependances Vagus
timestamp: 2026-08-29
id: c1bedca52504
---

# Manifeste de dépendances Vagus — inject/provide (spec interne v0.2)

type: regle
timestamp: 2026-08-27
tags: [vagus, plugins, dependencies, cordis, spec, skills]
links:
  - concepts/deepseek-harness.md
  - concepts/agent-plugin-standard.md
  - concepts/vagus-kg-v2.1.md

## Objet

Transposer les **coeffects réactifs** du paper Cordis (arXiv 2608.25512, §3.2)
dans la spec des skills/rôles Vagus : **déclaration d'abord, runtime plus tard**
(quand le KG devient référentiel unique). Chaque champ déclaré aujourd'hui est
l'**input exact** du runtime de demain (rollback LIFO, garde ¬relied) — sans
coût token (les specs vivent hors du prompt LLM).

**Ne PAS entrer dans plugin.json** (standard fermé agent-plugins.org, 10 champs) —
l'exporteur client l'exclut. Extension interne, portée par le frontmatter des
SKILL.md Hermes / les manifests de bundles Vagus.

## Format (frontmatter SKILL.md, section `x-vagus`)

```yaml
x-vagus:
  format_version: "0.2"            # OBLIGATOIRE — version inconnue = rejet
  namespace: custos                # paquet déclarant — jamais un namespace système
  provide:                         # clés fournies (ns:key[@version][:type])
    - custos:theme@1:interface
  writes:                          # clés MUTÉES = write-set (rollback futur)
    - custos:state@1:data
  inject:
    required:                      # absent → skill inactif (pas d'erreur)
      - llm:adapter
      - kg:custos
    optional: []                   # consommé si disponible ; n'active jamais
  disable_log:                     # optionnel — émis en CI
    reason: "dépendance indisponible"
    severity: warn                 # info | warn
```

Types de clé : `interface` (contrat d'API) | `data` (données). Défaut : `data`.
**Breaking change = nouvelle version de clé (`@2`), jamais de mutation de `@1`.**
Champ déprécié = marqué `deprecated` ici, retiré à la majeure suivante.

## Registre normatif des namespaces

| Namespace | Statut | Propriétaire / règles |
|---|---|---|
| `llm`, `kg`, `session`, `env`, `ssh` | **Système réservé** | Fournis par l'infrastructure SEULEMENT. Les skills peuvent injecter ces clés, JAMAIS les fournir, JAMAIS les déclarer en namespace |
| `custos` | Gouverné | Réservé aux skills du process CUSTOS (protocole anti-biais R1-R8 : lecture pure, ancrage calculatoire, pas de mémoire de session dans les chiffres) |
| `infra` | Gouverné | Réservé aux skills d'infrastructure (gateway, sandbox, déploiement) |
| `prism` | Gouverné | Réservé à la couche intelligence locale PRISM |
| autres | Libre | Premier déclarant (single-source) |

Clés système connues (injectables, non fournissables) : `llm:adapter`,
`kg:global`, `kg:custos`, `session:log`, `env:secrets`, `ssh:access`.
Hiérarchie : `kg:custos ⊆ kg:global` (vue, pas copie). Disponibilité :
`ssh:access` dépend du host (déclarer en optional hors VPS).

## Règles

1. **Namespacing obligatoire** : clé = `<namespace>:<nom>`. Jamais de clé nue —
   élimine la collision entre fournisseurs indépendants (Cordis §6.6).
2. **inject = demande de capacités** : un skill ne lit que ce qu'il déclare.
   **Le load time est l'unique point de décision capability-based (Cordis §6.4)** :
   toute clé non déclarée est inaccessible au runtime.
3. **provide : single-source** : une clé a UN seul fournisseur possible
   (discipline Cordis §4). Multiplicité = realms ou broker, pas de doublon.
4. **Dépendance absente = inactif, pas erreur** : required non satisfait →
   skill inactif (documenté, loggé en CI via disable_log). Réactivation =
   re-satisfaction quand la clé apparaît (sémantique runtime).
5. **Absence de cycle** : un cycle inject/provide (y compris transitant par une
   clé système) = les deux inactifs, détecté à la déclaration (Cordis §6.5).
6. **Écritures = effets** : `writes` = write-set déclaré. C'est l'input exact de
   l'accumulateur LIFO et de la garde ¬relied du futur runtime (Cordis §3.1, §3.2).
   Toute clé mutée non déclarée en writes = violation.

## Sémantique future (différée au runtime — documentée, pas implémentée)

- Rollback LIFO : décharger = appliquer l'accumulateur d'inverses en ordre inverse
- Garde ¬relied : le fournisseur survit à son consommateur (teardown sûr)
- Classification activating / deactivating / neutral par clé
- Table typée : validation de compatibilité provider/consumer au load time
- Realms : `env:secrets@telegram` — même clé, valeurs par contexte
- Interception read-only : contraintes right-biased sans modification
- Service broker : résolution par priorité quand multiplicité (au lieu d'inactivité)
- Re-satisfaction : surveillance de la table, réactivation automatique

## Conventions d'activation (tant qu'il n'y a pas de runtime)

- Le packaging (export_skill.py) **ignore** `x-vagus` : jamais dans plugin.json.
- Un skill avec `inject.required` manquant = marqué inactif dans les manifests
  de bundle Vagus (vagus-deployment-kit, kleia-up-kit) — décision de packaging.
- Les rôles (ANTIGRAVITY/OPENCODE/ARGOS) déclarent leurs inject via le bundle
  qui les embarque, pas dans le SKILL.md du rôle.

## Validation (contractualisée)

- Schéma unique : le validateur `workspace/agent-plugin-standard/validate_xvagus.py`
  EST le contrat (parsing unique validateur + doc).
- Checks : format_version, namespacing, réservés, single-source (scan global),
  inject résolus, types, writes, cycles (y compris via clés système),
  provides morts (warning), appartenance des namespaces gouvernés.
- Exit 0 = CONFORME. Le stress test global (`stress_plugin.py`) inclut ce check.

## Exemples (branches réelles, v0.2)

| Skill | namespace | provide | writes | inject.required |
|---|---|---|---|---|
| vagus-os-orchestration | vagus | vagus:fvp@1:interface, vagus:roles@1:interface | vagus:state@1:data | kg:global, session:log, prism:local-llm |
| redaction-custos | custos | custos:theme@1:interface | — | llm:adapter, kg:custos, session:log |
| custos-analyse-numerique | custos | custos:calculs@1:data | — | kg:custos |
| vagus-telegram-gateway-setup | infra | infra:telegram-gateway@1:interface | infra:gateway-state@1:data | env:secrets, ssh:access |
| couche-intelligence-locale | prism | prism:local-llm@1:interface, prism:cache@1:data | prism:cache@1:data | llm:adapter, kg:global |

## Statut

v0.2 — amendements du conseil du 27/08/2026 (P2 writes/version/type ; P3
format_version/registre/gouvernance ; P1 différé au runtime). Runtime :
planifié au moment où le KG devient référentiel unique.

Amendement du 28/08/2026 (council nocturne, cron) : périmètre gelé à 15
skills branchés (10 nouveaux, validateur CONFORME). Décision B1 :
`research/document-rag-ingestion` = doublon de `document-knowledge-ingestion`
(référence knowledge-workspace-architecture), **non branché, déprécié** —
fournisseur unique `document:ingestion@1:interface`. Roadmap de branchement
priorisée : journal `/tmp/xvagus-night-log.md` (cron 28/08).
