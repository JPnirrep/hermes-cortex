---
type: Concept
title: DeepSeek Harness (dsh)
timestamp: 2026-08-29
id: dcb02850ec75
---

# DeepSeek Harness (dsh)

type: veille-technologique
timestamp: 2026-08-27
tags: [deepseek, agent-harness, cordis, plugins, orchestration, veille]
links:
  - concepts/agent-plugin-standard.md
  - concepts/vagus-kg-v2.1.md
  - rules/manifeste-dependances-vagus.md

## Ce que c'est

Runtime agent open-source (MIT) de DeepSeek, dev preview v0.1, sorti 13/08/2026.
Record GitHub : 200K stars en 2 semaines, 22.8K forks. Node.js/TypeScript, pnpm monorepo (~50 packages).
Lancement : `npx @deepseek-ai/dsh web` → UI locale 127.0.0.1:3080. Local-first, clés API utilisateur.
Positionnement : « Model + Harness = Agent » — rival direct de Claude Code / Codex / Cursor.

## Architecture : tout est plugin

- Basé sur **Cordis** (meta-framework issu de l'écosystème Koishi) — paper arXiv 2608.25512
  « A Programming Paradigm for Spatiotemporal Composability » (Peking Univ + DeepSeek, 26/08/2026).
- Formalisation : **effets réversibles** (déchargement d'un plugin = retour arrière complet de ses effets,
  composabilité temporelle) + **coeffects réactifs** (dépendances inter-composants déclarées, activées/désactivées
  automatiquement, composabilité spatiale). Contexte unifié unique.
- Modèle, tools, skills, sessions, sandbox, storage, boucle d'agent, scheduling, UI = plugins remplaçables
  depuis la config (pas de core privilégié).
- **Profiles + bundles** : compositions nommées (web, headless, sdk, sdk-minimal, acp) = piles de bundles
  Cordis + patches de config (`cordis.patch.yml`) ; override par couches.
- **Seams (coutures de capacité)** : Service Definition / Service Provider / Consumer — un swap de provider
  change tout le produit (ex : sandbox local ↔ distant, subagents).
- **Session log append-only** = source de vérité ; invariant « Model-visible means logged ».
- **Sandbox** : Linux bwrap puis Landlock, macOS Seatbelt, Windows restricted token ;
  modes read-only / workspace-write / danger-full-access + escalation one-time approuvée par l'utilisateur.
- SDK TypeScript + Python (JSON-RPC) ; serveur ACP (Agent Client Protocol).
- Dogfooding massif : ~100 notes d'architecture dans `.agents/notes/` — l'équipe construit le produit avec des agents.

## Écosystème

1 100+ plugins communautaires catalogués en 3 jours (Oh-My-DSH), 2 600+ repos taggés `dsh-plugin`.
Majorité = skins/mèmes ; les plugins de fond (memory, web search) ré-implémentent ce qu'on a déjà.
Stratégie DeepSeek : open-source le harness pour distribuer les tokens (verrou d'écosystème).

## Pertinence Vagus OS

1. **Paper Cordis** (lu intégralement 27/08) = formalisation théorique de ce qu'on fait empiriquement — 3 mécanismes directement transposables (voir extraction ci-dessous).
2. **Pattern profiles + bundles + patches** + concept de **seam** → à étudier pour notre Agent Plugins 1.0.0.
3. **Sandbox Landlock** (bwrap→Landlock, modes + escalation) = exactement notre approche landlock-sandboxing — validation externe.
4. Session log append-only = aligné avec notre modèle de sessions.
5. Agnosticisme modèle validé : dsh branche n'importe quel endpoint OpenAI-compatible.

## Extraction Cordis → Vagus (paper lu intégralement 27/08/2026, 92p)

### Mécanisme 1 — Effets réversibles (composabilité temporelle, §3.1)
- Chaque effet = transformation de contexte + **inverse que le runtime détient** (pas l'auteur). Contexte d'effet ∂Γ = (état, accumulateur d'inverses φ) ; déchargement = appliquer φ → retour à l'état d'avant composition, garanti structurellement (Thm 7).
- **ctx.effect = unique primitive de mutation** (impl §5.1) : toute écriture (KG, mémoire, registrations) y passe → rollback par construction. Dispose auto-verrouillé, LIFO.
- **Inverse par-état retourné au point d'application** (pas d'undo uniforme) ; itérateurs d'effets = séquences reifiées (yield) — chargement = itérateur, déchargement = accumulateur.
- Undo sélectif possible ; cascade parent→enfant (décharger un hôte décharge ses enfants).

### Mécanisme 2 — Coeffects réactifs (composabilité spatiale, §3.2)
- Table de dépendances **typée par clé** Σ = (k:K)⇀V_k. **set() est lui-même un effet réversible** — la synergie : "coeffect operations are effects, and effects are revertible".
- Chaque changement de contexte classifié **activating / deactivating / neutral** contre la spec déclarée → activation = exécuter les effets, désactivation = appliquer l'accumulateur. Dépendance absente = inactif, pas erreur.
- **Garde ¬relied** (§4) : le fournisseur survit à son consommateur — un consommateur garde l'accès à sa dépendance pendant son propre teardown. Retrait différé après désactivation des consommateurs.
- **Isolation (realms)** : même clé résout différemment par contexte (multi-tenant, sandbox, tests). **Interception** : métadonnées right-biased — le contexte englobant contraint un composant sans le modifier, à chaud, sans reload.

### Mécanisme 3 — Contexte unifié + discipline de frontière (§3.3, §6.1)
- Γ∞ = (état, accumulateur, table coeffects) : toute interaction passe par UN médiateur. Équivalence observationnelle ≃ : récupération à ≃ près (message envoyé = envoyé).
- **Frontière intérieur/extérieur** : intérieur = modifiable exclusivement + restauré → réversible ; extérieur = non → idΓ. Un coeffect déplace la frontière (réifier une localité externe = la rendre réversible).
- Acquisition (dedans, réversible : open/fork) vs **émission** (dehors : write/send → compensation LIFO ou withholding). → Tout effet externe Vagus (fichier, API, message Telegram) doit être réifié en coeffect ou déclaré hors garantie.

### Décisions de design (§6) pertinentes pour nous
- **Capability-based** : un composant n'accède qu'aux clés déclarées ; capacités connues statiquement → revue au load time. Manifeste plugin (inject/provide) = demande de capacités.
- **Service broker** (vs binding exclusif) : swap de provider sans reload des consommateurs — rolling updates au niveau applicatif. Pour nos multi-providers LLM.
- **Cycle de dépendances = inactivité permanente prévisible** à l'install (pas de deadlock runtime) ; décomposition bidirectionnel → 2 cœurs + 2 intégrations ; bundling pour la granularité.
- **Versionnage** : namespacing des clés (K×paquet) + peer dependencies — drift d'interface et collision de clés sinon.
- **HMR transactionnel** : rechargement avec backup/restore, jamais d'état mi-rechargé. Confluence : l'état quiescent = f(conf finale) → réconciliation dans n'importe quel ordre, chargement concurrent.
- **Limitations avouées** : witness (inverse) non vérifié par le runtime = obligation auteur ; récupération à ≃ près ; état en mémoire non préservé par reload (DSU = futur) ; validation observationnelle mono-écosystème TS.

### Mapping Vagus (tableau)
| Mécanisme Cordis | Application Vagus |
|---|---|
| ctx.effect unique primitive | Toute écriture rôle/skill (fichiers, KG, registres) via primitive tracée → unload sans résidu |
| Accumulateur LIFO + cascade | Teardown ordonné automatique des rôles ; décharger un bundle décharge ses enfants |
| Coeffects typés + notify | Rôle déclare {llm_adapter, kg_access, session_log} → activation/désactivation auto |
| Garde ¬relied | ARGOS finit de lire les données pendant le retrait de leur fournisseur |
| Isolation realms | Vue KG par rôle ; sandbox test multi-tenant |
| Interception right-biased | Politique d'audit ARGOS contrainte par le contexte, sans modifier le skill |
| Capability-based | Manifeste Agent Plugins : inject/provide = capacités revues au load time |
| Service broker | Swap DeepSeek↔Gemini↔Mercury sans reload des consommateurs |
| Frontière + compensation | Message Telegram envoyé = émission → compensation, pas rollback |
| Versionnage clés | Namespacer les clés du KG par paquet déclarant |

## Verdict 27/08/2026

- Pas de migration (stack TS pré-alpha instable ≠ stack Python/Hermes).
- **Adopter** : (1) primitive d'effet tracé + accumulateur dans notre runtime de rôles ; (2) coeffects déclaratifs (inject/provide) dans la spec Agent Plugins 1.0.0 ; (3) pattern seam (profiles+bundles+patches) ; (4) namespacing des clés KG.
- Revoir dans 3-6 mois une fois la surface de compatibilité stabilisée.
