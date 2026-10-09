# 1-planificateur-production — moteur: qwen3.7-max

1. La chaîne de production recommandée, étage par étage
Étage 1 : Ingestion par Polling. Entrée : Dépôt de Sandrina dans le dossier kDrive « KLEIA-UP ». Sortie : Signal de déclenchement. Justification : kDrive (WebDAV Infomaniak) NE pousse PAS de webhook. n8n 2.42 doit donc utiliser un nœud Cron (coût zéro) couplé au remote rclone `kdrive:` pour scruter les nouveaux fichiers toutes les 15 minutes.
Étage 2 : Moulinage Cognitif et Sécurisation. Entrée : Texte brut ou note vocale transcrit. Sortie : `LIGNE-EDITO-REWRITTEN.md` scoré. Justification : Utilisation de l'API MISTRAL pour appliquer le moteur « JEV » (probabilité de partage, ancrage, adresse) et exécuter le détecteur de panne de ton (vérification stricte de la laïcité absolue et du ton doux HSP, zéro injonction).
Étage 3 : Génération des Artefacts. Entrée : Ligne éditoriale validée et scorée. Sortie : Script, `plan de tournage à cases` (HTML+PDF), liste d'images pour carrousel. Justification : S'appuie sur les skills existants (`tournage-face-camera`, `carrousel-social`, `redaction-post-social-kleia`) pour générer les plans structurés bloc par bloc, éliminant la charge mentale de JP.
Étage 4 : Dispatch et Push. Entrée : Artefacts générés. Sortie : Cartes Kanban et mise à jour du dashboard. Justification : Hermes reste le noyau cognitif via la CLI `hermes kanban` (tick 60s). Le système pousse les tâches vers l'interface locale (`server.py` + `app.js` de `semaine-41-travail`) pour offrir une façade facile et éviter les SaaS complexes.

2. Le calendrier et l'état d'avancement
Les états doivent calquer la structure d'`etat.yaml` déjà éprouvée dans `semaine-41-travail`, mais centralisés dans la board Hermes plutôt que dans des fichiers locaux éphémères qui meurent en fin de semaine.
États : 1. `LIGNE_BRUTE` (détection rclone), 2. `ACCORD_SANDRINA` (validation du hook), 3. `TOURNAGE_PRET` (génération du `plan de tournage à cases`), 4. `MONTAGE_FILMORA` (JP exporte vers Filmora Pro), 5. `PUBLICATION` (file d'attente Postiz).
Transitions : Chaque transition est horodatée dans `journal.jsonl`. Le tick de 60s d'Hermes lit ce journal pour mettre à jour le kanban. Si une transition stagne, `verifier.py` déclenche une alerte (détecteur de panne intégré).
Granularité : Macro-vue hebdomadaire (batching type `semaine-41-travail`), micro-vue journalière pour l'exécution. Le calendrier n'est pas une vue Gantt complexe, mais une liste chronologique de hooks retenus et signés dans `etat.yaml`, lisible sur le serveur web LOCAL.

3. Ce qui est automatisable vs ce qui doit rester humain
Automatisable (n8n + Hermes + Mistral) : Le polling kDrive, le scoring JEV, la génération du `plan de tournage à cases`, le dispatch dans Hermes, la détection de vocabulaire ésotérique (laïcité absolue), et la publication via `POSTIZ_API_KEY` (Postiz étant l'alternative open-source aux outils SaaS).
Humain - Sandrina : L'écriture de la ligne éditoriale initiale et la validation explicite du hook (`accord Sandrina` dans `etat.yaml`). Sa voix d'autrice HSP est unique, l'IA ne fait que la scorer et la structurer, jamais la rédiger ex nihilo pour éviter de trahir son ton.
Humain - JP : Le tournage face caméra (en suivant les cases à cocher), le montage dans Filmora Pro, et la supervision technique. JP ne doit jamais saisir de métadonnées ; il ne fait que cocher des cases dans le `plan de tournage à cases` ou cliquer sur "Fait" dans le kanban Hermes.

4. Cadence réaliste
JP est opérateur unique, gère la technique, le tournage et le montage sur Filmora Pro, avec un profil TDAH annoncé. Une cadence quotidienne est un échec garanti qui le fera perdre le fil.
Cadence recommandée : 1 journée de batch tournage (ex: mercredi, comme le dossier `production/mercredi-07`), produisant de 2 à 4 vidéos short ou carrousels. Suivie de 2 demi-journées de montage.
Fourchette justifiée : 2 à 4 contenus publiés par semaine. Au-delà de 4, le goulot d'étranglement du montage Filmora Pro et la fatigue décisionnelle du TDAH feront effondrer le pipeline. Le système n8n doit donc limiter les déclenchements à 4 slots hebdomadaires maximum.

5. Les 3 pièges de planification qui tueraient ce pipeline
Piège 1 : L'illusion du Webhook kDrive. Tenter de configurer un webhook sur Infomaniak kDrive échouera car kDrive NE pousse PAS de webhook. Sans le polling rclone via n8n 2.42, le système attendra une demande, violant la règle non négociable : « un dispositif qui attend ma demande est un échec ».
Piège 2 : La surcharge UI (Syndrome Notion/Buffer). Vouloir centraliser le calendrier dans un SaaS visuel. Buffer et Notion sont déjà rejetés car « pas faciles ». Le piège est de recréer une usine à gaz. La solution est de garder le petit serveur web LOCAL (`server.py` + `index.html`) alimenté par `etat.yaml` et Hermes.
Piège 3 : La trahison du ton HSP et la dérive ésotérique. Laisser Mistral générer des accroches sans garde-fou. Le ton doux et la laïcité absolue sont non négociables. Le détecteur de panne doit être un prompt de classification binaire (ésotérique/non-ésotérique, injonctif/doux) exécuté avant tout scoring JEV. Si ça échoue, le contenu est rejeté dans `ce_qui_ne_me_va_pas`.

6. Verdict : la chaîne MINIMALE viable en 1 semaine
Semaine 1 : Ne pas toucher à Postiz ni CANVA_MCP.
1. Configurer le Cron n8n 2.42 + rclone `kdrive:` pour lire le dossier « KLEIA-UP ».
2. Coder le nœud Mistral pour le scoring JEV et le filtre de laïcité absolue.
3. Générer automatiquement le fichier `etat.yaml` et le `plan de tournage à cases` (HTML) dans un dossier de sortie.
4. Connecter la CLI `hermes kanban` pour pousser ces tâches dans la board (default_assignee VIDE à remplacer par JP).
5. Intégrer `verifier.py` pour alerter si `etat.yaml` n'est pas mis à jour après 48h.
C'est le strict minimum pour que JP ait une vue qui POUSSE, sans effort de saisie, ancrée sur ses artefacts existants.