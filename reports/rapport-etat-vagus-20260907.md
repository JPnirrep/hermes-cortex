# Rapport d'État — Écosystème Vagus OS
## Cartographie complète · Crash test · KPI

**Date de génération :** 2026-09-07 23h45 (Europe/Paris)
**Collecte :** mesures live sur le VPS (`vps-f6868fc2-vps-ovh-net`), pas d'estimation.
**Method :** audit 9 couches (skill vagus-os-infrastructure-audit), cron DB, `ss`, `ps`, `docker`.

---

## 1 · Vue d'ensemble (KPI système)

| Indicateur | Valeur | Lecture |
|---|---|---|
| OS | Debian 12 (bookworm), kernel 6.1.0-50-amd64 | ✅ |
| Uptime | 61 jours, load 0.92 / 0.46 / 0.28 (6 CPUs) | ✅ stable, marge |
| RAM | 5.8 / 11 GiB utilisés, 5.6 GiB disponibles | ⚠️ 2 tiers consommés |
| Swap | 2 Go **100 % saturé** (448 Ko libres) | 🔴 dette confirmée |
| Disque `/` | 61 / 99 Go — **65 %**, 34 Go libres | ⚠️ surveiller |
| Conteneurs Docker | **20 running, 0 unhealthy, 0 exited** | ✅ excellent |

### Santé des services (crash test — ping/santé directe)
| Service | Port | État live |
|---|---|---|
| PRISM (RAG/compression) | 8650 | ✅ `{"status":"ok"}`, uptime 9,5 j |
| OMP MCP Gateway | 8644 | ✅ écoute |
| RecursiveMAS | 8651 | ✅ répond (GET non supporté = vivant) |
| Headroom (proxy LLM) | 8789 | ✅ 401 = auth requise, vivant |
| Hermes Gateway | 8642 | ✅ écoute (process `hermes`) |
| Hermes Dashboard | 9119 | ✅ écoute |
| Hermes WebUI | 8787 | ✅ écoute (process hermes-webui) |
| proxy LLM DeepSeek vision | 8790 | ✅ écoute |
| llama-server (SLM draft :11434, embed :18080) | — | ✅ 2 processus actifs |
| Agent Vault | 14322 | ✅ écoute 0.0.0.0 |

**20 conteneurs up :** transparence-citoyenne (api/worker×2/db/redis), n8n, kleia (db/frontend/backend/cache), brightbean-studio-worker, shared-postgres, temporal (admin/elasticsearch), postiz-redis, agent-vault, vaultwarden, lof-app. **Zéro unhealthy, zéro exited** → le crash test infra passe au vert.

---

## 2 · Couche Cron (27 jobs) — POINT CRITIQUE 🔴

| Statut | Nb |
|---|---|
| ✅ ok | 20 |
| ⚠️ `delivery_failed` (job OK, livraison vers plateforme morte) | 3 |
| ⚠️ livraison non résolue (status ok mais rien livré) | 1 |

### Les jobs en `delivery_failed` ou sans livraison — dette crash-test réelle
| Job | Horaire | Cause racine |
|---|---|---|
| **argos-watchman-daily** (le watchdog des livraisons !) | 06h00 quot. | `unknown platform 'webui'` → **n'alime personne** |
| **hygiene-token-log-hebdo** | 08h00 lun | `unknown platform 'webui'` |
| **custos-purge-rgpd** | 06h00 lun | `thread_id 1710 for telegram:6722033496 not found` → livré sans thread |
| **vagus-cleanup** | / 8h | `unknown platform 'webui'` (mentionné mais statut ok) |
| **Newsletter Kleia-up** | ven 14h | `no delivery target resolved for deliver=telegram` |

**Analyse :** 3 jobs ont `deliver` résolu vers la plateforme `webui` (inconnue du scheduler). Surtout **argos-watchman-daily** : le chien de garde censé ALERTER des livraisons ratées échoue lui-même à livrer — contradiction avec l'exigence de boucle fermée de JP. Ces jobs tournent, produisent leur sortie dans `cron/output/`, mais leur alerte n'atteint personne.

**Préconisation (correctif non appliqué ce soir, à valider) :** repointer `deliver` de ces 4 jobs vers `telegram:6722033496` (le chat DM réel de JP). Custos-purge-rgpd : retirer le `thread_id 1710` obsolète ou corriger le thread. Newsletter : renseigner le chat cible.

---

## 3 · Couche LLM & RAG

- **Chain décisionnelle DeepSeek V4 Flash (principal)** via Headroom 8789 → ✅ répond.
- **SLM local opérationnel** : llama-draft (qwen2.5-coder-1.5b, :11434), llama-embed (:18080) → ✅ coût 0 € / PRISM actif.
- **PRISM** : uptime 9,5 j, hook de compression/RAG actif → ✅.
- **Cron Mojo par mail (e2397ee9c662)** : a livré ce matin 07h45 à jpp180866@gmail.com (md+html) → **mécanisme mail SMTP validé**.

---

## 4 · Couche Mémoire / Contexte

- RAG : `watch_cortex.sh` **2 processus dupliqués** en cours (dette cosmétique, à nettoyer).
- Projet actifs workspace : site-web-kleia-up (MAJ aujourd'hui 19h15), LOF (12h06), custos, vigie-sante, hermes-vault.
- Rapport Mojo (06/09) présent dans cortex/reports.

---

## 5 · Dettes matérielles confirmées (répétition du 06/09)

La dette signalée dans le rapport Mojo du 06/09 **est toujours là** :
1. 🔴 **Swap 2 Go saturé à 100 %** (448 Ko libres) — premier à purger (RAM réelle du cache).
2. 🔴 **~1,5-2 Go RAM sur services quasi inertes** : java/elasticsearch ~773 Mo, 2× python3 ~818 Mo, temporal ~126 Mo.
3. 🟠 **`.cache` = 7,1 Go** (huggingface, chromium, playwright), `.hermes` = 7,2 Go → ~10-15 Go récupérables.
4. 🟠 **watch_cortex.sh dupliqué** (2 instances).

**Aucune de ces dettes n'a été traitée** depuis l'audit de la veille → plan de purge T0 toujours valide.

---

## 6 · Verdict du crash test

**Résultat global : ✅ système 61 jours de stabité, santé conteneurs parfaite (20/20), pas de service down, pas de panne API.**

**MAIS 2 points rouges qui cassent la boucle fermée JP :**
1. **Les alertes cron (watchdog inclus) ne livrent pas** — 3-4 jobs `deliver=webui` muets. C'est exactement le silence que l'on cherche à éviter.
2. **Swap plein** + RAM élastique inutile → risque de thrashing sous pic.

**Correctifs proposés (non exécutés ce soir — attendent ton GO) :**
- [ ] Repointer `deliver` de argos-watchman, hygiene-token, vagus-cleanup, purge-rgpd → telegram réel de JP.
- [ ] Purger swap / .cache / arrêter elasticsearch+temporal s'ils sont inertes.
- [ ] Dédoublonner watch_cortex.
- [ ] (Go RTK resté en suspens depuis 23h — non déployé, aucun GO clair.)

---
*Rapport produit par Hermes Agent — mesures live 2026-09-07 23h45. Dette partielle signalée en caveat : couche « skills mises à jour récemment » et « providers externes » restent les 2 seules couches non re-testeés en profondeur ce soir.*
