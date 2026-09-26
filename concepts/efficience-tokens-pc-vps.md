---
type: Concept
id: efficience-tokens-pc-vps
title: Stratégies d'efficience tokens PC + VPS — le poste de coût est une fuite cachée, pas un volume
timestamp: 2026-09-25
tags: [efficience, tokens, cout, fallback, moa, delegation, jev, slm, gate]
liens:
  - concepts/laya-moteur-decisions-local
  - concepts/laya-gate-suffisance-contexte
  - rules/prediction-avant-action
  - concepts/gate-semantique-non-testable
---

# Efficience tokens — ce qui a réellement été mesuré

## Le verdict qui contredit l'intuition

**Le poste de coût n'est pas le volume d'appels.** Mesure sur le mois 09/2026 ($1,98 au total) :

| Modèle / provider | Appels | Input facturé | Cache | Part non cachée |
|---|---|---|---|---|
| glm-5.3-flash / cometapi | 117 | 1 227 599 | 4 169 408 | **22,7 %** |
| glm-5.3-flash / custom | 27 | 434 622 | 749 824 | **36,7 %** |
| glm-5.3-flash / zai | 572 | 2 629 240 | 23 406 272 | 10,1 % |
| deepseek-v4-flash / deepseek | 610 | 1 802 672 | 36 601 984 | 4,7 % |
| deepseek-flash / deepseek | 195 | 688 828 | 16 663 552 | 4,0 % |

**Part de cache globale : 92,3 %.** Le cache fonctionne. Les appels DeepSeek sont bien cachés
(4-5 % d'input facturé) ; les appels GLM ne le sont pas (10-37 %) **et** leur coût n'apparaît
nulle part (registre Hermes à 0 $, `cost_source='none'` pour les providers agrégateurs).

## Les deux fuites trouvées

1. **`fallback_providers` nº1 = `glm-5.3-flash` (cometapi)** — sur le VPS **et** sur le PC, alors
   que le provider est interdit depuis le 04/09. Un fallback de tête s'exécute **souvent** : c'est
   un chemin d'exécution, pas une ligne de config inerte. Il consommait 1,23 M de tokens non cachés.
2. **`moa.presets.default.aggregator` = `glm-5.3-flash`** — 60 appels à ~10 051 tokens d'input
   **non cachés** (603 K tokens) dans une seule session. Un agrégateur de tournoi reçoit tous les
   prompts de référence : c'est structurellement le plus gros consommateur d'input non caché.

## Le principe transférable

**Un levier d'efficience se vérifie en mesurant le VOLUME et la PART NON CACHÉE, par couple
(provider, modèle) — pas en comptant les appels, et pas en faisant confiance au registre.**
Le registre Hermes est aveugle (`cost_source='none'`) précisément là où se concentre le coût :
sur les providers agrégateurs. Un poste de coût « à 0 $ » au registre qui consomme 1,2 M de
tokens est le pire cas possible — il est cher **et** invisible.

Corollaire de diagnostic : `grep` sur les configs des **deux hôtes** pour tout modèle interdit.
Un provider interdit en politique peut survivre des mois en fallback sans que personne ne le voie.

## Ce qui est en place

- `scripts/routeur-delegation.py` — routes **mesurées** (SLM pour classify/extract/titre/tags/
  resume-court/rewrite ; distant obligatoire pour redaction/raisonnement/code/decision/suffisance).
  Tâche non répertoriée → distant par défaut (prudence, pas d'optimisme).
- `scripts/efficience-gate.py` — 3 contrôles : provider interdit actif, fuite d'input (> 25 % sur
  gros input), transports (SLM/JEV/PRISM). **Silencieux** au repos, alerte Telegram sinon.
  Cron `Efficience Gate` (6 h, no_agent, 0 €). Version PC : `C:\Users\JP\efficience-gate-pc.py`
  + tâche planifiée `HermesEfficienceGate` (Ready).
- JEV **opérationnel** (appel réel 200, 515 ms, $0,0000148) — clé posée dans le `.env` du profil,
  plafond 10 $, 9,9949 $ restants. Ne jamais journaliser la valeur.

## Les deux pièges d'alerte (ils rendent un dispositif muet)

1. **Cron créé depuis le WebUI** : `deliver: origin` hérite `{"platform": "webui"}` que le
   scheduler rejette (`unknown platform 'webui'`) → `last_status: delivery_failed`, message jamais
   parti. Toujours forcer `telegram:<chat_id>` pour une alerte.
2. **Alerte permanente sur une absence structurelle** : le PC n'a aucune couche locale
   (11434/18080/8650/8790 tous muets — vérifié). Sonder ce qui n'existe pas produit une alerte
   qu'on ne peut pas éteindre, donc qu'on apprend à ignorer. `LOCAL_ATTENDU = False` côté PC.

## Ce qui n'est PAS fait (et pourquoi)

- **Laya en pré-filtre de contexte** : récusé en zero-shot (voir `laya-gate-suffisance-contexte`),
  il juge l'apparence de suffisance. À reprendre après fine-tune, pas avant.
- **Le PC n'a pas de couche locale** : y installer un SLM serait un chantier, pas un réglage.
  Sa stratégie retenue = cloud seul + gate.
