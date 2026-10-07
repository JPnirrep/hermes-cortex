---
type: Reference
id: 3c15a38276f8
title: Tunnel SSH Windows
tags: [infra, ssh, windows]
timestamp: 2026-09-18
owner: vagus
links: [telegram-bot.md]
---
## Mécanique
- VPS 135.125.53.215. PC-JP initie `ssh -N -R 2222:localhost:22 debian@135.125.53.215`.
- Port 2222 VPS → SSH du PC. Accès VPS : CLI `~/.local/bin/hermes-windows` (ls/cat/get/put/exec/mount/info) + socket `/tmp/cua-win.sock` (service systemd `cua-win-bridge`, socat → 2222 → cua-driver bureau Windows).
- Clé PC autorisée : `jpjp@PC-JP` ED25519 SHA256:CD6cJWdIHEalIiTFEhlRi9i1VsTEqd7QsQUFFPpCed8 (authorized_keys, sans option restrict).
## Tâche Windows
- Tâche planifiée « HermesReverseTunnel » → wrapper `C:\Users\JP\scripts\hermes-tunnel.bat` (boucle ssh -N -R + retry 5 s via `ping -n`, ServerAliveInterval=30/CountMax=3, ExitOnForwardFailure=yes, ConnectTimeout=15, ExecutionTimeLimit illimité), déclencheurs Boot + Logon (délai 30 s), principal JP/Interactive/Limited.
- Garde-fou « HermesReverseTunnelGuard » (S4U, Time répétition 5 min) : sonde `:2222` côté VPS et relance la porteuse — nécessaire car un trigger Logon+répétition ne rejoue pas après un kill du `cmd`. Recréation idempotente : `C:\Users\JP\scripts\register-tunnel-task.ps1`.
- ⚠ Le doc d'origine (wrapper `bin\hermes-reverse-tunnel.cmd`, `/SC ONSTART`) est périmé : le runbook de référence est `~/tools/hermes-reverse-tunnel-recovery.md` + skill `windows-ssh-tunnel`.
## Livraison sans le tunnel (ajouté 06/10/2026)
- Le pont tombe sans prévenir (constaté : DOWN 13:10 → UP 14:52, alerte Telegram du watchdog). Ne pas bloquer une livraison : déposer les fichiers dans le cloud de JP (kDrive kleia-up, drive 3622226, rclone `kdrive:`) dans un sous-dossier explicite du dossier de travail, puis armer un **pousseur automatique** (boucle 30 s qui attend `ss -tln | grep :2222`, purge le montage mort, copie, compare les tailles, écrit un reçu).
- Vérification indépendante obligatoire de toute livraison : tailles VPS/PC, `ffprobe` **lu depuis le disque PC** via le montage, et `head -c 40M | md5sum` comparé pour les gros médias. `hermes-windows put` tronque silencieusement (270 Mo → 36 Mo).
## Diagnostic (18/09/2026 16h09, procédure envoyée par mail à JP pour OMP)
- Symptôme : sessions sshd actives (polling) MAIS 127.0.0.1:2222 Connection refused. Cause : tâche Windows pas relancée.
- Check VPS : `ss -tln | grep ':2222'` + `hermes-windows info`.
- Pièges : bind fantôme sur 2222 (ExitOnForwardFailure fait quitter), pas de doublon de tunnel, GatewayPorts=no → bind loopback uniquement.
## Vigilance
- Watchdog : `tools/tunnel-watchdog.sh` (cron */5) alerte Telegram UP/DOWN 2222 + 8790.
- Gmail OAuth token profil vagus = REVOKED (invalid_grant, 18/09/26) → envois mail via SMTP app-password (`GMAIL_USER`+`GMAIL_APP_PASSWORD`, pattern vigie-sante) en attendant ré-auth OAuth.
- Procédure complète : `workspace/procedure-tunnel-omp/` (md + script d'envoi).
