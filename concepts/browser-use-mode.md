---
type: Concept
id: e3dec5a295fc
title: Mode Browser Use (CLI 3.0)
tags: [browser, scraping, tokens, infra]
timestamp: 2026-08-11
owner: vagus
links: [windows-ssh-tunnel.md]
---

Analyse stratégique de la mise à jour CLI 3.0 (vidéo youtu.be/y82TL0GsTZE, 11/08/26).

## Règle d'usage browser_exec
- **À privilégier** : collecte multi-éléments structurée avec interaction suivie (scraping de masse sur une plateforme). Gain mesuré : -61 % tokens (fourchette annoncée 48-66 %).
- **À proscrire** : lecture de page unique / contenu statique → ~2× plus coûteux que les outils classiques.

## Matrice VPS vs Local
| Critère | VPS | Local (IP résidentielle) |
|---|---|---|
| Anti-bot | Faible (IP cloud identifiées/bloquées : YouTube, X, Instagram) | Forte |
| Cas d'usage | Sites légers sans JS lourd (Wikipedia, blogs statiques, RSS, API JSON) ; Firecrawl pour rendu JS modéré (Shopify, Next.js) | Scraping complexe réseaux sociaux / vidéo / sites protégés |

## Implications écosystème
- Scraping YouTube/X/Instagram lourd → passer par [poste local JP](windows-ssh-tunnel.md) (IP résidentielle), pas par le VPS.
- Cron cost-zéro : le monitor_url (GET borné) reste la voie par défaut pour pages uniques — jamais browser_exec en cron.
- Liens : [Windows Reverse SSH](windows-ssh-tunnel.md), [Protocole de collaboration](protocole-collaboration.md)
