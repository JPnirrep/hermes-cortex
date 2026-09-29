---
type: decision
id: laya-decommission-2026-09-28
timestamp: 2026-09-28
tags: [laya, decommissionnement, calibration, ece, mesure, dettes-techniques]
links:
  - concepts/laya-moteur-decisions-local.md
  - concepts/laya-gate-suffisance-contexte.md
  - concepts/jev-typesafe-sources-2026-09-23.md
  - concepts/jev-titulaire-poste-decision-2026-09-28.md
  - rules/prediction-avant-action.md
---

# Décommissionnement de Laya — 28/09/2026

## Décision
Laya (NandhaKishorM/laya) est **retiré du système**. Motif de JP : « ça n'apporte rien
d'extra à notre système ». Confirmé après mesure sur décisions réelles.

## La mesure qui tranche (3 jours de collecte, 603 labels utilisables)
| Indicateur | Valeur | Référence naïve |
|---|---|---|
| ECE sur `answer_confidence` | **0,8048** | — |
| Accuracy au seuil 0,7 | **16,8 %** | constante « jamais » = 83,9 % |
| Brier | **0,7765** | baseline constante = 0,1350 |
| Distribution `p_livrera` | 509 / 603 à ≈ 1,00 | — |
| `answer_confidence` moyen | 0,966 (min 0,570) | — |

Le moteur prédit « livrera » à ~1,0 quasi systématiquement alors que la réalité est 16 %.
**5,8× pire que la baseline constante.** Ce n'est pas un défaut de calibration, c'est une
incapacité de discrimination sur cette cible.

## Deux leçons distinctes (ne pas les confondre)
1. **Le fit du 25/09 était dégénéré.** 28 labels dont ~1 négatif : ECE 0,137 et « 100 %
   d'accuracy à 70 % de couverture » étaient un artefact du taux de base, pas un signal.
   → *Règle : ne jamais accepter un fit sous 200 labels, même quand le résultat est flatteur.*
   Un résultat flatteur sur un jeu dégénéré est une alerte, pas une validation.
2. **La cible comptait « a parlé », pas « a réussi ».** Le label était
   `delivery_outcome IN (delivered, failed)` alors que 98,6 % des tirs sont `suppressed`
   (sortie vide = silence voulu). Laya répondait correctement à la question posée — la
   question n'était pas la bonne. → *Avant de juger un moteur, vérifier que le label mesure
   ce qu'on croit qu'il mesure.*

## Empreinte retirée (mesurée, `df` avant/après)
- `/home/debian/laya-env` venv — 5,6 Go (laya + torch 1,2 Go + nvidia 3,2 Go + triton 897 Mo)
- `/home/debian/laya_models` checkpoints HF — 2,3 Go
- `/home/debian/laya-src` clone — 11 Mo
- **Total : ~8 Go** (disque : 74 Go → 66 Go, 79 % → 70 %)
- Crons supprimés : `0204450ee7e2` Laya Shadow Gate, `d67016cc6ba0` Laya Shadow Report
- Scripts supprimés : `laya-shadow-gate.py`, `laya-shadow-report.py`, `laya-adequacy-gate.py`

## Correctif de fond (pas une simple suppression)
`routeur-delegation.py` sondait le venv Laya (`transport_laya`). Le laisser aurait affiché
un transport mort en ❌ permanent dans `statut` → faux négatif dans le routeur de décision.
Retiré dans la même passe : fonction `transport_laya`, entrée `VENV_SITE`, et le poste
`suffisance` porte désormais le motif de décommissionnement.

## Le poste n'est pas vacant
Avec Laya hors jeu, **JEV reste seul titulaire du poste « décision typée »** — même API,
mêmes primitives, mais lui décide réellement. Voir
`concepts/jev-titulaire-poste-decision-2026-09-28.md`. Ne pas combler un besoin futur de
décision typée avec le SLM local (greffier, pas décideur).

## Ce qui survit d'utile
- **L'archive** `~/backups/laya-decommission-20260928/` (3,8 Mo) : scripts, JSONL de 762
  prédictions, rapports, script de fit. C'est la preuve du verdict.
- **La procédure de mesure** : le shadow gate était un dispositif passif correct ; c'est la
  cible qui était mauvaise. Réutilisable pour évaluer tout futur moteur de décision.
- **Le pattern du détecteur de panne** : `laya-shadow-report.py` a détecté sa propre panne
  (cadence, backfill, volume) et a alerté sans être sollicité. Ce patron est à reprendre.

## Dette détectée pendant l'opération
- **`[DETTE]` Cron runner ≠ shebang** : le runner cron exécutait `laya-shadow-gate.py` avec
  **Python 3.14** alors que le shebang pointait vers `/home/debian/laya-env/bin/python`
  (3.11) → `ModuleNotFoundError: numpy._core._multiarray_umath`, 3 tirs en échec.
  Un script cron qui dépend d'un venv doit **vérifier et forcer son interpréteur**, ou être
  appelé explicitement via `<venv>/bin/python script.py`. Le shebang seul ne suffit pas.
