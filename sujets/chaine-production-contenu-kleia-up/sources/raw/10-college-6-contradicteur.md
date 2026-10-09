# 6-contradicteur — moteur: o4-mini

1. Objections de fond  
   1.1 Déclencheur absent : kDrive NE pousse PAS de webhook (état réel vérifié) ; n8n (docker n8nio/n8n:2.42.0, up 10 jours) ne peut pas détecter automatiquement le dépôt de Sandrina sur kDrive sans une solution externe (rclone – mais sans événement – ou cron + verifier.py).  
   1.2 Répartition floue des tâches : la board kanban Hermes intégrée (CLI `hermes kanban`, default_assignee VIDE) produit des cartes sans responsable automatique, donc aucune garantie qu’un élément du « Moulinage » (vérif. cohérence, consultation planning) soit toujours assigné à JP.  
   1.3 Automations incomplètes : les skills (montage-video-rs, carrousel-social, tournage-face-camera, visuels-post-social, redaction-post-social-kleia, publication-rs-sandrina) existent, mais il n’existe aucun workflow n8n stocké ni exporté pour connecter ces étapes ; chaque pipeline devra être codé de zéro dans n8n.  
   1.4 Publication non solvée : Buffer et Notion ont été rejetés ; POSTIZ_API_KEY est présente, mais aucun conteneur Postiz n’est en fonctionnement pour remplacer Buffer (aucune instance détectée). Sans conteneur Postiz, l’étape push social reste manuelle.  
   1.5 Risque de tonalité : la clé MISTRAL est disponible, mais tout contenu IA généré hors de la ligne édito de Sandrina (LIGNE-EDITO-REWRITTEN-20261005.md) court le risque de trahir son ton doux HSP++ (aucun système de supervision IA+humain n’est en place pour garantir l’alignement de style).

2. Dépendances humaines cachées  
   2.1 Si Sandrina retarde le dépôt de sa ligne édito (mail / note vocale / dossier kDrive), l’ensemble du pipeline stagne dès l’étape 1 (aucun trigger ne peut initier sans son contenu).  
   2.2 Si JP ne maintient pas l’instance n8n (mises à jour, sauvegardes, surveillance uptime) ou si le docker n8nio/n8n:2.42.0 tombe en panne, le « Moulinage » ne se lancera plus et le dispositif perd son caractère « push ».  
   2.3 L’absence de monitoring continue du serveur local (server.py + index.html + app.js) et du script verifier.py limite la détection automatique de panne ; JP doit manuellement relancer ces composants chaque semaine.  
   2.4 La planification cron (coût-zéro) repose sur la précision de la configuration sur la machine de JP ; si son environnement Debian change (upgrade, déplacement de dossier /home/debian/workspace/sandrina-strategie/), toutes les tâches planifiées tombent en défaut.  
   2.5 L’organisation des artefacts semaine par semaine (production/mercredi-07, semaine-41-travail/) implique que JP crée et archive de nouveaux dossiers manuellement : sans sa discipline, les anciens dossiers périment, cassant la continuité.

3. Coût caché (maintenance, dette, temps de JP)  
   3.1 Création & debug des workflows n8n (écriture JS/HTTP, tests, logs, alertes) : 2–4 heures/semaine (justifié par la complexité des 5 sorties attendues du moulinage et l’absence de flux existants).  
   3.2 Maintenance Hermes & scripts Cron (mise à jour CLI, correctifs, supervision des tickets 919 journaliers via `hermes kanban`) : 1–2 heures/semaine.  
   3.3 Surveillance de l’instance Docker n8n (logs, redémarrages, backup du volume) : 1–2 heures/semaine (typique des conteneurs en production légère).  
   3.4 Support à Sandrina pour valider l’output IA & vérifier la tonalité (revue hum. de chaque script généré, 5–10 textes/mois) : 1–2 heures/semaine.  
   3.5 Total estimé : 5–10 heures/semaine de surcharge pour JP (hors production créative Filmora Pro), soit 20–40 % d’une demi-journée par semaine.

4. Scénario « on ne fait rien »  
   4.1 JP continue à produire visuels/vidéos sans vue transverse ni historique consolidé (actuel : dossiers locaux éphémères semaine par semaine, /home/debian/.../production).  
   4.2 Pas de checklist centralisée (« OK, clic, c’est fait »), ce qui maintient la douleur exprimée (« je travaille à l’aveugle »).  
   4.3 Le système tel quel « fonctionne », la marque publie, mais la fatigue de JP (TDAH) s’accroît : pas d’amélioration, pas de risque immédiat de rupture de chaîne (production manuelle persiste).  
   4.4 Avantage de stabilité : pas de dette technique supplémentaire, pas de coûts d’infra. Inconvénient : aucune progression vers l’automatisation promised, burn-out potentiel de JP.

5. Probabilité d’usage dans 3 mois  
   5.1 Complexité multipliée (n8n + rclone/cron + Hermes + scripts ad hoc) génère de la dette.  
   5.2 Sensibilité de JP au contexte dispersé : si la charge dépasse 10 h/sem, il abandonnera.  
   5.3 Taux d’adhésion estimé à 35 % :  
       - 20 % de chance si n8n chute ou si Sandrina demande une révision manuelle constante,  
       - +15 % si JP s’astreint au suivi « push » malgré la charge.  
   5.4 Raisonnement : pipeline multidépendant, maintenance forte, faible effet d’accroche sans interface unifiée.

6. Verdict : condition SINE QUA NON  
   Implémenter un déclencheur événementiel fiable (webhook ou équivalent) au dépôt de Sandrina : remplacer kDrive par un stockage capable de push (GitLab/GitHub, Nextcloud avec webhook, S3+Lambda) ou intercaler un microservice de watch-folder. Sans trigger natif, tout le pipeline demeure manuel et ne pourra « pousser » Hermes comme cerveau unique.