---
type: Concept
id: infra-graph-v1
title: Graphe d'infrastructure — dépendances Vagus OS
description: Graphe typé inféré automatiquement des dépendances réelles du VPS. Permet de répondre à « qu'est-ce qui tombe si X disparaît » au lieu de « probablement rien ».
tags: [graphe, infrastructure, dependances, kpi, argos, prediction]
owner: vagus
created_at: 2026-09-13
updated_at: 2026-09-13
version: 1.0
---

# Graphe d'infrastructure

## Ce que c'est
Un graphe typé des dépendances réelles du VPS, **inféré automatiquement** depuis
le système vivant — pas maintenu à la main. Un graphe manuel dérive en trois
semaines et se met à mentir avec autorité.

## Pourquoi c'est le levier principal
Sans graphe, la réponse à « quelles sont les conséquences de cette action ? »
est locale : « ce fichier sera écrit ». Avec graphe, la réponse est en chaîne :
« ce secret alimente 3 scripts, qui alimentent 2 services, dont dépend un cron
de nuit ». C'est exactement le passage de la prédiction locale à la prédiction
de chaîne.

## Sources d'inférence (toutes locales, lecture seule, coût zéro)
| Source | Nœuds produits | Arêtes produites |
|---|---|---|
| `cron/jobs.json` | cron Hermes | depends_on, delivers_to, requires_secret |
| `scripts/` | script | consumes, requires_secret |
| systemd (user + system) | service | depends_on, part_of, listens_on |
| `.env` | secret (**nom seul**, jamais la valeur) | requires_secret |
| `docker ps` | container | listens_on |
| `ss -tlnp` | port, process | listens_on |
| `crontab -l` | cron_sys | depends_on |

## Types d'arêtes
- `depends_on` — le nœud source cesse de fonctionner si la cible disparaît
- `requires_secret` — dépendance à une clé (jamais à sa valeur) ;
  `implicit: true` = dépendance de provider déduite, pas d'appel direct
- `consumes` — lecture d'un fichier/dossier/port
- `delivers_to` — canal de livraison externe
- `listens_on` — port d'écoute
- `part_of` — appartenance à un répertoire

## Test de validité
La seule mesure qui compte : *« si je supprime ce nœud, quels nœuds tombent ? »*
doit renvoyer une **liste**, pas un haussement d'épaules.

```bash
python3 ~/hermes-cortex/tools/build-infra-graph.py --impact DEEPSEEK_API_KEY
python3 ~/hermes-cortex/tools/build-infra-graph.py --impact "Healthcheck VPS"
```

## Limites assumées
- **Config drift** : le graphe est un instantané. Reconstruire après tout
  changement structurel (nouveau cron, nouveau service, changement de port).
- **Dépendances implicites** : les appels réseau sortants vers des APIs
  externes ne sont détectables que par les providers déclarés, pas par
  inspection du trafic.
- **Chemins construits dynamiquement** : quand un script utilise une variable
  (`DB="$PROFILE/state.db"`) au lieu d'un littéral, la dépendance n'est pas
  inférée. C'est la cause principale des ~175 nœuds feuilles. Corollaire
  opérationnel : **le graphe est fiable pour les dépendances structurelles
  (cron→script, service→script, script→secret, conteneur→port) et lacunaire
  pour les dépendances de données.** Ne pas conclure « aucun impact » sur un
  dossier de données : vérifier à la main.
- **Le monde extérieur** : rien hors du VPS n'est couvert. Les conséquences
  sociales, réputationnelles et humaines restent hors modèle — c'est
  précisément le rôle du journal de prédiction de les mesurer empiriquement.

## Liens
- [Journal de prédiction](journal-prediction.md) — consommateur du graphe
- [Hermes Cortex index](../index.md)
