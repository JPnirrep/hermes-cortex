---
type: regle
id: e8f73e717d45
timestamp: 2026-08-18
tags: [log, invariant, auditabilite, custos, hygiene]
---

# Invariant « model-visible means logged »

Tout ce que le modèle voit (system prompt, messages, tool results, injections)
doit être reconstructible depuis le log (state.db, append-only). C'est la
discipline du session log — pompée du framework dsh (DeepSeek Harness), 18/08/26.

## Vérification (script)

```bash
python3 ~/.hermes/profiles/vagus/scripts/log-reconstruct.py --latest 45   # rapport
python3 ~/.hermes/profiles/vagus/scripts/log-reconstruct.py --check       # cron, silencieux si RAS
```

Règles appliquées par le script :
- system_prompt présent + hash résolu via table `system_prompts`
- message assistant vide : OK si `finish_reason` présent (réponse coupée = état loggé, PAS une violation)
- user vide : issue (jamais observé depuis 18/08/26)
- tool results : troncatures marquées dans le contenu (21 cas historiques, tous tracés)

État au 18/08/26 : 49/49 sessions analysées reconstructibles (0 dette).

## Applications

- CUSTOS R1-R8 (passe aveugle, sources citées) : n'importe quelle session de
  production peut être auditée/rejouée — la traçabilité est vérifiable, pas déclarée.
- H8 : toute session non reconstructible = dette technique → tag `[DETTE]` dans log.md.
- Cron `hygiene-token-log-hebdo` (lundi 8h, no_agent) alerte sur violations.

## Liens

- skill: garde-fous-tokens (token-meter replay-aware — même famille, même log)
- concept: custos-doctrine (exigence de transparence des sources)
- regle: jp-workflow (exactitude factuelle vérifiable)
