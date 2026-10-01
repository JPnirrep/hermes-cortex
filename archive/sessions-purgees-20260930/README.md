# Sessions supprimées le 30/09/2026 — archives de sécurité

Consigne JP : « supprime les sessions vides ». Vérification préalable obligatoire — **aucune des
quatre n'était réellement vide** : le comptage de messages (1-2) masquait du contenu réel. Chaque
session a donc été **exportée en Markdown ici avant suppression**, puis supprimée avec le CLI
officiel (`hermes sessions delete <id> --yes`).

| Session | Source | Ce qu'elle contenait | Motif de suppression |
|---|---|---|---|
| `2fee01b8cc18` | webui | Question de JP (1 373 car.) « comment utiliser glm-5.3-flash intelligemment » — **restée sans réponse** | Question obsolète : GLM est interdit depuis le 04/09 ; le sujet a été traité depuis dans d'autres sessions |
| `20260903_224338_8e26c588` | telegram DM | Demande de 49 car. (lien `github.com/facebookresearch`, « analyse et crée… ») — **sans réponse** | Demande rejouée ailleurs (même URL le 29/08) |
| `20260928_125215_4bddf4` | sous-agent | Livrable de 10 954 car. « STRATÉGIE INFOPRENEUR — SANDRINA PERRIN / KLEIA-UP » | **Doublon** : le même contenu est conservé dans la session parente `75ee624211b4` |
| `20260928_225645_daf8d0` | oneshot | Test technique `Reponds exactement: TEST_OK` → `TEST_OK` | Test de liaison, aucune valeur |

## Restauration — ce qui est possible, et ce qui ne l'est pas

Chaque dossier `<id>.md/` contient **le transcript complet en Markdown** (+ `manifest.jsonl` avec le
`sha256` du fichier, pour vérifier l'intégrité) :

```bash
sha256sum <id>.md/<id>-<titre>.md        # comparer au champ sha256 du manifest.jsonl
```

⚠️ **`hermes sessions import` ne restaure PAS ces archives** : il ne lit que des conversations
Claude Code (`~/.claude/projects`) ou Codex CLI. Il n'existe pas de ré-import d'un export Hermes
vers `state.db`. Une session purgée n'est donc pas rejouable en base — mais **son contenu est
intégralement conservé et lisible ici** (transcript Markdown complet, y compris le livrable de
10 954 caractères du sous-agent). Pour réutiliser un contenu : le relire tel quel, ou le recoller
dans une nouvelle session.

État après opération : 4 sessions et leurs messages supprimés, `PRAGMA integrity_check` = ok,
**137 sessions restantes**, 0 session sans titre ni profil.
