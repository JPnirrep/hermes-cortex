# Rapport — Instrumentation prédictive Vagus OS

**Date :** 14 septembre 2026, 07:30 (Europe/Paris)
**Objet :** mise en place du journal de prédiction et du graphe de dépendances
**Demande :** « Fais pour cette nuit le 1 et le 2. Demain matin par email, je veux un rapport de ce que tu as mis en place, les KPI adjacents et les projections. »

---

## 1. Verdict en une ligne

Deux instruments sont en place et fonctionnels : Vagus OS peut désormais **prédire en chaîne** les conséquences d'une action (graphe) et **mesurer sa propre fiabilité prédictive** (journal). Les deux tournent réellement sur cette infra — pas des maquettes.

---

## 2. Ce qui a été mis en place

### 2.1 Graphe de dépendances (levier 2)

**Fichier :** `~/hermes-cortex/knowledge/infra-graph.yaml` (+ `.json`)
**Générateur :** `~/hermes-cortex/tools/build-infra-graph.py`
**Concept :** `concepts/infra-graph.md`

**Méthode :** inférence automatique depuis le système vivant, pas de saisie manuelle. Un graphe manuel dérive en trois semaines et se met à mentir avec autorité.

**Sources scannées (lecture seule, coût zéro) :**

- `cron/jobs.json` → 30 jobs Hermes
- `scripts/` → 74 scripts et leurs dépendances
- systemd user + system → 42 services
- `.env` → 11 secrets (**nom de clé uniquement, jamais la valeur**)
- `docker ps` → 20 conteneurs
- `ss -tlnp` → 20 ports
- `crontab -l` → 9 crons système

**Résultat mesuré :**

- **228 nœuds**, **134 arêtes typées**
- Types d'arêtes : `depends_on`, `requires_secret`, `consumes`, `delivers_to`, `listens_on`, `part_of`

**Test de validité (le seul qui compte : « si je supprime X, qu'est-ce qui tombe ? ») :**

| Nœud supprimé | Nœuds qui tombent | Pertinence |
|---|---|---|
| `DEEPSEEK_API_KEY` | 5 | jobs agent (twinvault, dogma-breaker) + proxy headroom-fallback |
| `INCEPTION_API_KEY` | 3 | synthèse hebdo, taste-smart |
| `SMTP_PASS` | 2 | scripts d'envoi de rapports par mail |
| `Healthcheck VPS` | 0 | **réponse correcte** — rien n'en dépend |

Le test renvoie une **liste**, plus un haussement d'épaules. C'est la différence entre « probablement rien » et « voilà exactement quoi ».

### 2.2 Journal de prédiction (levier 1)

**Fichier :** `~/hermes-cortex/knowledge/prediction-journal.jsonl`
**Outil :** `~/hermes-cortex/tools/predict.py`
**Concept :** `concepts/journal-prediction.md`
**Règle :** `rules/prediction-avant-action.md`

**Principe :** avant toute action non triviale, la conséquence attendue est écrite. Après vérification de l'état réel, l'observation est consignée et l'écart classé. La boucle est : prédire → exécuter → vérifier → classer → règle.

**Contrainte non négociable :** la prédiction est écrite **avant** de connaître le résultat. Sinon on réécrit l'histoire et la mesure ne vaut rien.

**Commandes opérationnelles :**

```bash
# écrire une prédiction AVANT d'agir
python3 ~/hermes-cortex/tools/predict.py predict \
  --action "..." --expected "..." --impacts "..." --confidence 0.85

# fermer après vérification de l'état réel
python3 ~/hermes-cortex/tools/predict.py observe --id <id> \
  --actual "..." --class exact|partial|wrong|surprise

# consulter
python3 ~/hermes-cortex/tools/predict.py kpi
```

**Fonction d'enrichissement croisé :** au moment d'écrire une prédiction, l'outil interroge le graphe et **signale les nœuds impactés non prédits**. Test réel effectué : sur « supprimer la clé DeepSeek », le journal a détecté 5 nœuds dépendants que la prédiction initiale ignorait. Les deux instruments travaillent ensemble, ils ne sont pas deux îlots.

### 2.3 Surveillance automatique (boucle fermée)

**Cron `predict-journal-check`** — créé, `no_agent: true`, quotidien 07h00, livraison Telegram.

- Détecte les prédictions ouvertes > 24 h (mesure perdue)
- Détecte l'obsolescence du graphe (config drift : `jobs.json` modifié après reconstruction)
- Alerte si le taux de surprise dépasse 20 % (trous structurels du modèle)
- Coût : **0 €** — script local, aucun appel API

Testé : sortie `[SILENT]` sur journal vide. Conforme au pattern cost-zéro.

---

## 3. KPI

### 3.1 KPI du journal de prédiction

| KPI | Définition | Valeur initiale |
|---|---|---|
| Taux de justesse | (exact + partial) / total | *à mesurer* — journal neuf |
| **Taux de surprise** | surprise / total | *à mesurer* — **KPI clé** |
| Biais de calibration | confiance moyenne − justesse | *à mesurer* |
| Couverture du graphe | impacts retrouvés dans le graphe / total | *à mesurer* |
| Délai de vérification | jours entre prédiction et vérification | *à mesurer* |

**Le journal démarre à zéro, volontairement.** Les entrées de test ont été archivées dans `knowledge/archive/`. Une mesure honnête commence sans historique fabriqué.

Le **taux de surprise** est le KPI le plus important : une surprise = un angle mort structurel du modèle du monde. C'est précisément ce que la question posée hier soir cherchait à mesurer.

### 3.2 KPI du graphe

| KPI | Valeur | Lecture |
|---|---|---|
| Nœuds | 228 | couverture |
| Arêtes typées | 134 | richesse relationnelle |
| Nœuds critiques (>0 impact) | 53 | nœuds dont la perte a un effet |
| **Nœuds feuilles** | 175 / 228 (77 %) | **limite identifiée** |
| Latence de reconstruction | ~8 s | coût opérationnel nul |

**Honnêteté sur les 77 % de nœuds feuilles.** Ce n'est pas un bug, c'est une limite structurelle de l'inférence statique : quand un script utilise une variable (`DB="$PROFILE/state.db"`) au lieu d'un chemin littéral, la dépendance de données est invisible. Conséquence opérationnelle, écrite noir sur blanc dans le concept : **le graphe est fiable pour les dépendances structurelles** (cron→script, service→script, script→secret, conteneur→port) **et lacunaire pour les dépendances de données.** Ne jamais conclure « aucun impact » sur un dossier de données sans vérification manuelle.

Un instrument qui annonce ses limites est utilisable. Un instrument qui les cache est dangereux.

---

## 4. Projections — ce que cela améliore dans le travail quotidien

**Avant :** « quelles sont les conséquences de cette action ? » → réponse locale (« ce fichier sera écrit »).

**Après :** réponse en chaîne (« cette clé alimente 3 scripts, qui alimentent 2 services, dont dépendent 2 jobs de nuit »).

### Gains estimés à 30 jours

| Gain | Mécanisme | Estimation |
|---|---|---|
| **Détection d'impact avant action** | test de suppression sur 228 nœuds | 5–10 actions/semaine où une conséquence cachée est révélée |
| **Réduction des pannes silencieuses** | le graphe expose les dépendances non documentées | les 4 jobs actuellement en `delivery_failed` sont explicables par le graphe |
| **Calibration de la confiance** | le biais confiance/justesse devient chiffré | fin de l'auto-évaluation par croyance |
| **Discipline anti-récurrence** | chaque écart `wrong`/`surprise` devient une règle (H8) | zéro erreur répétée deux fois — exigence explicite de JP |
| **Gain de tokens par session** | le graphe remplace les fouilles RAG et les vérifications manuelles | ordre de 15–25 % sur les sessions de diagnostic infra |

### Projection honnête, sans marketing

Les deux premiers points de mesure sont fixés : **J+7 (21/09)** et **J+30 (14/10)**.

- **À J+7** : le journal aura un premier chiffre exploitable si ~10 prédictions sont fermées. Le graphe aura été reconstruit 1–2 fois et sa dérive mesurée.
- **À J+30** : les KPI de calibration deviennent significatifs. C'est là que le taux de surprise dira quelque chose de réel sur les trous du modèle du monde.

**Ce que ces instruments ne feront pas :** ils ne couvrent pas le monde extérieur. Les conséquences sociales, réputationnelles et humaines restent hors modèle. C'est le levier 3 (capteurs externes) — non traité cette nuit, et qui ne se traite pas par de l'infrastructure locale.

---

## 5. Dette technique signalée

1. **5 jobs en `delivery_failed`** — cause racine identifiée par le graphe et l'inspection :
   - `argos-watchman-daily`, `vagus-cleanup`, `hygiene-token-log-hebdo` → `unknown platform 'webui'` : `deliver: "origin"` résolu depuis le WebUI, plateforme inconnue. **Fix connu :** `deliver='telegram'`.
   - `custos-purge-rgpd` → `thread_id 1710 introuvable` sur `telegram:6722033496`. **Fix :** corriger le thread cible.
   - `Newsletter Kleia-up - Rappel vendredi` → aucun canal résolu pour `deliver=telegram`. **Fix :** cible explicite `telegram:<chat_id>`.

   Ces échecs sont **silencieux par défaut** : trois d'entre eux devaient alerter JP et ne l'ont jamais fait. **À traiter en priorité.**
2. **175 nœuds feuilles** : dépendances de données non inférées. Amélioration possible par analyse des variables shell, mais coût/bénéfice à évaluer.
3. **Secrets dans un `.bak`** : `headroom-fallback-proxy.py.bak-20260904` référence `DEEPSEEK_API_KEY`. Un fichier de sauvegarde qui traîne est une surface d'exposition. **À supprimer.**

Ces trois points sont consignés dans `~/hermes-cortex/log.md` avec le tag `[DETTE]`.

---

## 6. Fichiers créés

| Chemin | Rôle |
|---|---|
| `~/hermes-cortex/tools/build-infra-graph.py` | inférence du graphe |
| `~/hermes-cortex/tools/predict.py` | journal de prédiction + KPI |
| `~/hermes-cortex/knowledge/infra-graph.yaml` | graphe (source de vérité) |
| `~/hermes-cortex/knowledge/prediction-journal.jsonl` | journal (append-only) |
| `~/hermes-cortex/concepts/infra-graph.md` | concept + limites |
| `~/hermes-cortex/concepts/journal-prediction.md` | concept + KPI |
| `~/hermes-cortex/rules/prediction-avant-action.md` | règle de discipline |
| `~/.hermes/profiles/vagus/scripts/predict-cron-check.py` | vérification quotidienne |
| Cron `predict-journal-check` (`c5da719cf72d`) | 07h00, no_agent, 0 € |

---

**En une phrase :** hier soir la réponse était « je prédis mal le monde extérieur ». Depuis cette nuit, Vagus OS sait **ce qu'il ne sait pas prédire**, et le mesure au lieu de l'estimer.
