---
type: Concept
id: b7567e5a023e
title: Pattern — Action Review avant écriture externe
tags: [agents, securite, idempotence, patterns, openmuse]
timestamp: 2026-09-26
owner: vagus
links: [pattern-lease-receipt.md, pattern-pglite-services-legers.md, deepseek-harness.md]
source: CopilotKit/OpenMuse apps/server/src/actions.ts (MIT, alpha 15/09/26)
---

Pattern extrait d'OpenMuse, retenu comme le plus transposable à l'écosystème Vagus. Il répond à une question que tout agent qui écrit vers l'extérieur doit trancher : **comment empêcher un doublon d'action irréversible sans bloquer l'utilisateur dans une boucle de validation ?**

## Le contrat en 4 points

1. **Proposition, pas exécution.** L'agent ne « fait » pas : il produit une `ActionProposal` typée et hashée. L'exécution est un second temps, déclenché par une décision humaine explicite (approve / reject), elle-même persistée.
2. **Idempotency key = SHA-256 de la clé fournie.** Deux propositions avec la même clé donnent le même id. Un rejeu ne crée pas de doublon — il retombe sur la proposition existante.
3. **Liaison par version.** La proposition est liée à la version de la cible (`targetVersion`) et à la connexion (`connectionId`). Si la cible change entre proposition et exécution, la proposition est invalidée. Pas d'écriture sur un état périmé.
4. **Expiry + liaison de propriétaire.** Chaque décision est bornée dans le temps et scopée à un propriétaire. Un changement de compte ou une déconnexion invalide le travail en attente lié.

## La règle dure

> **Aucun rejeu caché après une écriture externe incertaine.**

Si l'écriture vers le fournisseur (mail, calendrier, API tierce) revient dans un état ambigu — timeout, réponse partielle, statut inconnu — on NE rejoue PAS. On expose l'incertitude et on demande de vérifier le résultat côté fournisseur avant de recréer quoi que ce soit. Le coût d'un doublon (deux relances envoyées au même apprenant, deux rendez-vous créés) est supérieur au coût d'une vérification manuelle.

Corollaire : *annuler ou mettre en pause empêche les étapes SUIVANTES ; une requête fournisseur déjà approuvée et en vol peut aboutir.* Le système ne prétend pas annuler l'inannulable.

## Application Vagus

- **Kleia-up** : envoi de conventions de formation, relances d'apprenants, création d'événements calendrier, relances OPCO. Toute action sortante passe par une proposition revue.
- **LOF** : publication réseaux sociaux — l'humain valide le texte exact qui sera publié, la version est liée au post cible.
- **CUSTOS** : envoi d'un thème à un client. Irréversible côté perception : jamais d'envoi automatique.
- **Cron** : un cron ne doit JAMAIS déclencher une écriture externe irréversible sans étape de revue. La revue peut être un fichier déposé dans un dossier `pending/` que JP approuve — le prix d'un aller-retour vaut mieux qu'un doublon.

## Anti-pattern correspondant

Retry automatique décoré en « robustesse ». Un retry sur une écriture non idempotente est un générateur de doublons. Sur une écriture idempotente (PUT avec clé), le retry est acceptable — la clé fait le travail.

## Lien

- Suite logique : [Pattern — Lease + Receipt](pattern-lease-receipt.md) pour la partie exécution durable.
- Variante infra : [Pattern — PGlite](pattern-pglite-services-legers.md).

Source analysée : dépôt OpenMuse (MIT), commit 34b15bc, 26/09/26. Non adopté comme produit (dépendance CopilotKit Intelligence hors MIT, mono-utilisateur) — pattern retenu uniquement.
