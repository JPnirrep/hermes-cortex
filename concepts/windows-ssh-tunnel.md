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
- Tâche planifiée « HermesReverseTunnel » → wrapper `C:\Users\JP\bin\hermes-reverse-tunnel.cmd` (boucle ssh -N -R + retry 15s, ServerAliveInterval=30/CountMax=3, ExitOnForwardFailure=yes), /SC ONSTART.
## Diagnostic (18/09/2026 16h09, procédure envoyée par mail à JP pour OMP)
- Symptôme : sessions sshd actives (polling) MAIS 127.0.0.1:2222 Connection refused. Cause : tâche Windows pas relancée.
- Check VPS : `ss -tln | grep ':2222'` + `hermes-windows info`.
- Pièges : bind fantôme sur 2222 (ExitOnForwardFailure fait quitter), pas de doublon de tunnel, GatewayPorts=no → bind loopback uniquement.
## Vigilance
- Watchdog : `tools/tunnel-watchdog.sh` (cron */5) alerte Telegram UP/DOWN 2222 + 8790.
- Gmail OAuth token profil vagus = REVOKED (invalid_grant, 18/09/26) → envois mail via SMTP app-password (`GMAIL_USER`+`GMAIL_APP_PASSWORD`, pattern vigie-sante) en attendant ré-auth OAuth.
- Procédure complète : `workspace/procedure-tunnel-omp/` (md + script d'envoi).
