# 7-briseur — moteur: o4-mini

1. Le renversement proposé  
Instaurer un atelier synchrone hebdomadaire (présentiel ou visioconférence) de 3 heures pour co-produire en temps réel tous les livrables (script, plan de tournage, plan de montage, liste d’images, bonnes pratiques), remplaçant entièrement la logique de dépôt‐déclencheur‐pipeline.

2. Pourquoi la chaîne actuelle est structurellement condamnée  
- kDrive (WebDAV Infomaniak) « kdrive: » ne génère aucun webhook (état réel), rendant n8n 2.42.0 inopérant pour détecter un dépôt (état.yaml/journal.jsonl).  
- Les artefacts (/home/debian/…/semaine-41-travail/, plan-tournage-short-sandrina-15oct/) sont locaux, éphémères et isolés, sans continuité transverse.  
- Hermes kanban (CLI `hermes kanban`, tick 60s, default_assignee VIDE) n’est alimenté qu’à la main et reste vide par défaut.  
- JP perd le fil dès que les fichiers se multiplient (profil TDAH), Buffer et Notion ont déjà été rejetés pour leur manque de simplicité.  
- L’absence de push automatique et de vue continue rend le suivi incomplet : pas de calendrier unifié, pas de checklist vraiment intégrée.

3. Ce que le renversement change concrètement  
Pour JP :  
- Une seule source de vérité pendant 3 heures (zoom ou salle), plus de documents épars sur kDrive,/workspace et artefacts hebdo.  
- Visibilité instantanée : script finalisé en direct, plan de tournage validé bloc par bloc (comme dans plan-tournage-short-sandrina-15oct/), checklist « OK, clic » réalisée en séance.  
- Hermes sert de tableau d’accompagnement post-atelier, non d’outil principal.  

Pour Sandrina :  
- Voix d’autrice préservée, elle rédige et valide en direct sans craindre un texte IA incohérent (MISTRAL ou CANVA_MCP optionnels, générés en séance si nécessaire).  
- Ton doux garanti : feedback immédiat de JP, sans injonctions rébarbatives.  

4. Ce qu’il coûte : ce qu’on abandonne  
- L’orchestration n8n (docker n8nio/n8n:2.42.0) pour les triggers automatiques sur kDrive.  
- Les artefacts journaliers (journal.jsonl, donnees.yaml, etat.yaml, server.py) qui capturent la granularité fine des actions, désormais remplacés par un compte-rendu synthétique post-atelier.  
- L’usage potentiel de POSTIZ_API_KEY ou BUFFER_API_KEY pour la publication automatique ; tout se planifie manuellement lors de l’atelier.  
- La fausse impression de continuité des fragments locaux ; on sacrifie l’historique automatisé minute par minute.

5. Pourquoi ce n’est PAS une optimisation déguisée  
- Ce n’est pas « ajouter un outil » ni « réordonner » des étapes : on supprime l’architecture asynchrone entière pour la remplacer par une session unique de co-création.  
- Pas d’empilement d’automatisations (n8n, Cron, rclone, Hermes en boucle) : on bascule vers un schéma humain-centré, sans reliance sur les événements file system.  
- C’est une rupture, non un ajustement de cadence : on abandonne la promesse d’un pipeline « push » technologique pour un vrai « push » social, où JP et Sandrina se rendent disponibles ensemble.

6. Verdict : à tester même partiellement ?  
Oui.  
Piloter une session hebdomadaire de 3 heures la semaine prochaine, avec ordre du jour fixe :  
• 30 min de revue de la ligne édito déposée (LIGNE-EDITO-REWRITTEN-20261005.md).  
• 60 min de rédaction du script final.  
• 30 min de construction du plan de tournage et de la checklist.  
• 30 min d’attribution des tâches et calendrier partagé.  
Cette expérimentation permettra de valider immédiatement la rupture et de mesurer son impact sur la visibilité d’avancement et le confort de chacun.