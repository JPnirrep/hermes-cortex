# 4-ux-charge-cognitive — moteur: mimo-v2.6-pro

1. Diagnostic : pourquoi Buffer et Notion échouent pour JP

Buffer et Notion ont été rejetés au motif « pas faciles » — ce n'est pas un goût, c'est une incompatibilité de modèle. Trois échecs distincts :

(a) **Pull contre push.** Les deux outils exigent que JP ouvre l'app, trouve la bonne vue, et attendent son action. Or la règle non négociable du contexte est explicite : « un dispositif qui attend ma demande est un échec ». Le déclencheur attendu est le dépôt de la ligne édito par Sandrina (mail / note vocale / kDrive), pas l'ouverture d'un onglet par JP. Aucun des deux outils ne réagit à ce dépôt. Et kDrive « NE pousse PAS de webhook » : la seule brique capable de transformer un dépôt en événement est n8n 2.42 (polling IMAP/WebDAV), déjà en fonctionnement depuis 10 jours.

(b) **Modèle mental imposé.** Notion impose de concevoir sa propre base : databases, propriétés, relations, vues. Avant d'obtenir la moindre information utile, il faut configurer. Pour un profil attention, c'est du travail de bureau déguisé en travail de production. Or le format qui a *déjà* fonctionné pour lui existe : le plan-tournage-short-sandrina-15oct est structuré « bloc par bloc AVEC cases à cocher ». Le modèle mental gagnant est connu, il ne reste qu'à l'industrialiser.

(c) **Charge de rangement + impermanence.** Les artefacts sont par semaine, locaux, et « meurent en fin de semaine » : LIGNE-EDITO-REWRITTEN-20261005.md, semaine-41-travail/ (etat.yaml, donnees.yaml, journal.jsonl, server.py), production/mercredi-07/ (LISEZ-MOI par production). Notion n'aurait rien résolu : il aurait fallu réimporter chaque semaine à la main, ce qui viole la règle de poussée. Le vrai problème est structurel : absence de vue transverse, pas absence d'outil.

Buffer, lui, cible la toute fin de chaîne (publication), alors que la douleur exprimée est en amont : « je travaille vraiment à l'aveugle, je n'ai pas de vue de calendrier ni d'avancement de la création ». BUFFER_API_KEY est présente mais ne servira qu'à l'étape 4 (publication-rs-sandrina), jamais de surface de travail. POSTIZ_API_KEY n'est même pas déployée (aucun conteneur Postiz détecté) — elle ne doit pas devenir un prétexte à ajouter une UI.

2. Les 6 propriétés d'un outil « sympa » pour un opérateur unique TDAH

1. **Push intégral.** La surface se présente à lui : notification quand le dépôt de Sandrina est mouliné, quand une tâche arrive, quand quelque chose coince. Jamais l'inverse. Ancrage : règle utilisateur citée plus haut.
2. **Zéro rangement exigé.** Aucune décision de classement. Les fichiers typés existent déjà (etat.yaml par jour, donnees.yaml, journal.jsonl horodaté) : c'est le cerveau qui range, pas l'opérateur. Ancrage : « il perd le fil quand tout est éparpillé ».
3. **Une seule action possible par ligne, binaire.** Formulaire verbatim de JP : « OK, clic, c'est fait ». Une case à cocher, pas de statut à 6 valeurs, pas de champ libre. Langage doux, zéro injonction, laïcité absolue (règle de ton liée à Sandrina HSP).
4. **Persistance transverse.** La semaine 41 ne disparaît pas à la semaine 42. Les fragments hebdomadaires sont le symptôme ; la surface doit cumuler les semaines dans un seul état.
5. **Détecteur de panne visible dans la surface.** « Chaque dispositif de mesure doit inclure son propre détecteur de panne » : pastille de dernière synchronisation, rouge si n8n ou le dispatch kanban n'a rien envoyé depuis N minutes. Un outil muet est pire que pas d'outil.
6. **Coût zéro au repos.** Tout ce qui tourne en continu = cron cost-zéro (n8n 2.42 déjà up). MISTRAL (génération IA) reste ponctuel et payant, déclenché par le dépôt de ligne édito, jamais par une souscription.

3. La façade concrète : où JP regarde, quoi il clique

**Où** : le petit serveur web LOCAL déjà existant — server.py + index.html + app.js de semaine-41-travail — industrialisé en instance unique permanente, ouverte en onglet épinglé du navigateur. C'est la même page en permanence, jamais une nouvelle fenêtre.

**Pourquoi PAS un nouvel outil dédié** : Buffer et Notion ont déjà été rejetés sur critère de simplicité ; un sixième outil = nouveau mot de passe, nouveau modèle mental, nouvelle fenêtre. JP est opérateur unique : aucune fonctionnalité collaborative n'a de valeur. Les briques fonctionnelles sont déjà assemblées et testées une semaine par lui-même. Postiz absent, Canva_MCP non sollicité pour l'affichage.

**Quoi il clique** :
- En haut : bandeau « cette semaine » avec jauge d'avancement + pastille « dernière synchro » (détecteur de panne).
- Corps : liste du jour issue de etat.yaml (hook retenu/signé, accord Sandrina, publié, urls, métriques), une case par tâche.
- Onglet « productions » : ouvre les LISEZ-MOI (production/mercredi-07, IDs kDrive, formats, facteurs d'agrandissement) et le plan de tournage à cases en HTML/PDF.
- Onglet « à traiter » : les sorties du moulinage (script à lire pour Sandrina, plan de montage Filmora Pro, liste d'images pour carrousel + mode opératoire).
- Aucune saisie libre, aucune page de réglage.

Refus explicite d'un canal type Telegram/Discord comme surface principale : le push y est natif, mais il n'y a pas de vue calendrier — exactement la douleur exprimée. La notification est la sonnette, la page est la table.

4. « Le cerveau est Hermes » traduit en UX

Concrètement : **la façade ne décide de rien, ne calcule rien, ne stocke rien**. Elle est une projection de Hermes (board kanban `hermes kanban`, dispatch auto, tick 60s) et de n8n 2.42. Les skills (montage-video-rs, carrousel-social, tournage-face-camera, visuels-post-social, redaction-post-social-kleia, publication-rs-sandrina) produisent les artefacts ; la page les expose.

Conséquences UX :
- Chaque ligne de tâche porte le nom du skill qui l'a produite : JP ne rédige pas, il exécute un livrable déjà sorti (script à lire, plan de montage, liste d'images).
- Le bouton « mouliner » n'existe pas : le déclenchement est le dépôt de ligne édito, pas une action de JP.
- **Angle mort structurel à corriger** : `default_assignee` de Hermes est VIDE. Les tâches dispatchées sans assignataire sont invisibles pour JP. Traduction UX : toute tâche non assignée apparaît en tête de page dans un bandeau « à prendre », sinon le cerveau la perd silencieusement.
- Toute logique métier (cohérence, planning, bonnes pratiques plateformes) vit dans n8n/Hermes ; la page ne contient aucune règle modifiable par JP. C'est ce qui la rend « sympa » : elle ne lui demande jamais de penser à l'outil.

5. Test de friction

(a) **Marquer « c'est fait »** : 1 écran (page déjà ouverte, onglet épinglé), 1 clic sur la case, retour visuel immédiat, sauvegarde dans etat.yaml via l'API du serveur local, 0 saisie, 0 navigation. Cible : 1 clic, 0 rafraîchissement. Comparaison Notion : ouvrir l'app → trouver la base → ouvrir l'item → cocher → retourner à la liste = fourchette 5-7 interactions, non mesurée dans le contexte (je n'ai pas de mesure, c'est une estimation structurelle à valider par test).

(b) **Voir l'avancement de la semaine** : 0 clic si la jauge est dans le bandeau haut permanent ; 1 clic si elle est dans un onglet. Cible : 1 écran, ≤2 clics, <3 secondes perçues. Aucune navigation dans des dossiers semaine-41-travail/ — la transversalité est structurelle, pas une vue à reconfigurer.

6. Verdict

**La surface unique : une page web locale unique (server.py + index.html + app.js industrialisés), onglet épinglé, alimentée en continu par Hermes (board kanban) et n8n 2.42, poussée par notification navigateur, avec bandeau haut = semaine (jauge + pastille de panne) et liste du jour = checklist binaire issue de etat.yaml.** Ni Buffer, ni Postiz (non déployé, et de toute façon fin de chaîne), ni Notion. BUFFER_API_KEY reste pour l'étape publication via publication-rs-sandrina, en sortie, jamais en surface de travail. Le format cases à cocher du plan de tournage est le standard de toutes les listes. Le seul ajout fonctionnel réel : corriger le `default_assignee` vide de Hermes (bandeau « à prendre ») et brancher le dépôt kDrive/mail sur n8n — sans quoi la chaîne reste sourde et l'opérateur, à l'aveugle.