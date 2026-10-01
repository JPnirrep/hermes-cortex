---
type: regle
id: 4c9ab71e2f03
timestamp: 2026-09-30
tags: [cout, cometapi, mimo, facturation, arbitrage, provider]
---

# Facturation CometAPI — grille vérifiée et champ `usage.cost` non fiable

Règle de calcul du coût LLM chez CometAPI (relevé + mesure contrôlée du 30/09/2026).
Relie à [efficience tokens PC/VPS](../concepts/efficience-tokens-pc-vps.md), où le poste
dominant est la relecture de cache — c'est le paramètre qui décide de l'arbitrage.

## Ce qui est facturé (vérifié sur la facturation réelle)

Appel témoin de 23 408 tokens d'entrée, delta `total_usage` = 0,2624 → **0,112 $/M**,
soit exactement la grille CometAPI (−20 % sur le tarif officiel Xiaomi 0,14/0,28).
Le tarif officiel aurait donné 0,3277 : c'est donc bien la grille Comet qui est appliquée.

| $/1M | GLM-5.3-Flash | MiMo-V2.6-Flash | DeepSeek off-peak | DeepSeek peak |
|---|---:|---:|---:|---:|
| entrée (miss) | 0,120 | **0,112** | 0,150 | 0,300 |
| entrée (cache hit) | 0,024 | **0,0022** | 0,003 | 0,006 |
| sortie | 0,400 | **0,224** | 0,600 | 1,200 |

MiMo domine sur les trois composantes, à toute heure : **aucun arbitrage horaire ne peut
battre CometAPI sur MiMo**. La grille complète est dans
`~/.hermes/profiles/vagus/scripts/pricing.json` (clé par couple `provider/modèle`).

## Le piège : `usage.cost` surévalue la facture

Le champ `cost` renvoyé par `/v1/chat/completions` est calculé à ~0,175 $/M d'entrée et
surévalue la facture d'environ 55 %. **Ne jamais budgéter à partir de ce champ.** Les deux
sources fiables sont la grille `pricing.json` et `total_usage` de
`/v1/dashboard/billing/usage` (unité : centimes de dollar, lisible avec la clé API — le
quota de la console exige un token de session).

## Règle de mise à jour

Tout relevé tarifaire doit être confirmé par une mesure contrôlée (appel de ~20k tokens,
delta `total_usage`) avant d'être écrit dans `pricing.json` et marqué `verified: true`.
Un chiffre de page web n'est pas une preuve de facturation — cf.
[provider-cost-forensics](../../.hermes/profiles/vagus/skills/maintenance/provider-cost-forensics/SKILL.md).