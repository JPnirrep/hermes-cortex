---
type: concept
id: laya-decision-engine-2026-09
timestamp: 2026-09-25
tags: [laya, decisions-typees, calibration, routage, prism, cout-zero, github-audit]
links:
  - concepts/jev-typesafe-sources-2026-09-23.md
  - concepts/gate-acceptation-skills-vagus.md
  - rules/prediction-avant-action.md
---

# Laya — moteur de décisions typées local (ConvAI Innovations)

## Ce que c'est
Moteur de décision **non-autorégressif** : encodeur bidirectionnel (ModernBERT-large 421M / mmBERT-base 322M),
**un seul forward pass**, 3 primitives typées — `choice`, `score`, `noul` (=P(vrai)).
Aucune génération de texte => rien à parser, rien à halluciner. Les sorties sont des probabilités.
Repo canon : `NandhaKishorM/laya` (Apache-2.0, 23 407⭐). Checkpoints : HF `convaiinnovations/laya{,-multilingual,-typed-decisions}`.
Antagoniste direct de **Jev** (TypeSafe AI) — et API serveur **identique** (`POST /v1/systemone`).

## Pourquoi retenu (mesuré, pas cru)
- **203 ms/question en CPU pur** (VPS Haswell 6 cœurs, zéro GPU) vs **852 ms** pour DeepSeek en réseau payant.
- **Coût 0 €**, hors ligne, souverain — aucune dépendance à un fournisseur.
- **type_acc 87,5%** sur nos questions de décision (jeu du banc Noul).
- Serveur HTTP + **serveur MCP** fournis => branchement Hermes natif.

## Le point qui compte : la confiance est un signal exploitable
Mesuré sur 12 cas étiquetés (banque de questions `r4-bench/bench_noul.py`) :
- Les **2 erreurs portent une confiance de 0,46** — le modèle ne se trompe pas en étant sûr.
- **Seuil 0,70 => 100% d'accuracy sur 75% de couverture.**
- Deux notions à ne PAS confondre :
  - `answer_confidence` = P(réponse rapportée) → **ECE 0,073** (bon) → **c'est celle-ci qu'il faut utiliser pour gater**.
  - `confidence` = 1−entropie normalisée → ECE 0,192 (mauvais) → mesure la concentration, pas la justesse.

## Les pièges (documentés par les auteurs eux-mêmes)
1. **Calibration shippée invalide** : le bucket `choice:11+` du checkpoint vaut 0,1006, hors plage [0,5 ; 5] → clampé à 0,5 → **bucket non calibré**. Le code prévient : *« a caller gating on confidence is told a coin flip is a certainty »*. README : ECE 0,466 → 0,081 **seulement après refit**. `laya-multilingual` n'a **aucune** température fittée.
2. **Zero-shot faible** : « a fast base to specialise, not a zero-shot decision engine » — 0,362 vs 0,318 au hasard. Le 0,766 annoncé vient d'un fine-tune sur le train split du bench.
3. **Choix >20 options** : effondrement (Banking77 : 0,425 vs 0,870 Jev) — budget de tokens partagé par les libellés.
4. **Labels booléens interdits** (`true`/`false`, `yes`/`no`) en `choice` : les checkpoints suivent le libellé au lieu de la description. Utiliser des libellés sémantiques ou opaques (`A`/`B`).
5. **`agent.temperature` est mutable à chaud** → le refit de calibration par bucket est faisable chez nous, gratuitement, sur nos labels.

## Usage prévu chez Vagus
1. **Gate de routage PRISM** : si Laya est confiant (answer_confidence ≥ seuil sur nos labels), la décision est prise **localement à 0 €** ; sinon escalade DeepSeek. Gain visé : ~75% du trafic décisionnel à coût nul.
2. **QC laïcité / classification CUSTOS** en local (noul calibré).
3. **Pré-filtre cron** : décisions de triage sans appel API.

## Gate passif en production (GO JP 25/09/2026)

**Adopté : T=1 sans refit, gate sur `answer_confidence` ≥ 0,7.** Cron `Laya Shadow Gate`
(`0204450ee7e2`, every 4h, no_agent, deliver local) → `~/.hermes/profiles/vagus/scripts/laya-shadow-gate.py` :
- Passe 2 : 1 question `noul` par job cron actif (28/jour) : « ce tir livrera-t-il une sortie ? »
- Passe 1 (backfill) : labels réels via `executions.db` (`delivery_outcome` du 1er tir postérieur à la prédiction ;
  `delivered/failed`=True, `suppressed`=False, 48h sans tir=`no_fire`).
- Données : `~/r4-bench/results/laya_shadow_labels.jsonl` — ~400 labels en 2 semaines → refit vers le 09/10/2026.
- **Limite honnête** : 98,6 % des tirs sont `suppressed` (crons silencieux) → le label est quasi déterministe
  par job. L'accuracy du gate ne sera pas informative ; c'est la **calibration (ECE/Brier) sur labels
  minoritaires** qui fera foi. Le shadow ne décide rien : il ne mesure que.

## Conditions d'adoption
- [x] Fitter la calibration par (type, nb d'options) sur ~200 labels **avant** tout gating — testé sur 40 cas synthétiques le 25/09 : le fit n'améliore pas (ECE 0,137→0,153), refit différé aux ~200 labels réels du gate passif.
- [ ] Ne pas dépasser ~10-20 options en `choice` sans fine-tuning.
- [ ] Libellés sémantiques, jamais booléens.
- [x] Sortir le venv du scratch (purgé 72 h) si adopté → `/home/debian/laya-env` (25/09).

## Preuves
- Mesures : `r4-bench/results/laya_probe_20260925.json`, `r4-bench/results/laya_calibration_20260925.json`, `r4-bench/results/laya_fit_calibration.json`
- Scripts : `~/r4-bench/{laya_probe,calib_probe,test_serve,fit_laya_calibration}.py` (sortis du scratch 25/09)
- Gate passif : `~/.hermes/profiles/vagus/scripts/laya-shadow-gate.py` (selftest intégré, verrou /tmp, stdout silencieux)
