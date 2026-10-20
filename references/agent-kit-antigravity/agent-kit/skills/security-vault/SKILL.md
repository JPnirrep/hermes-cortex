---
name: Security Vault
description: Chiffrement et gestion sécurisée des secrets (clés API, credentials) inspiré d'Open Jarvis.
---

# 🔐 Security Vault

Ce module assure que tes secrets ne sont jamais exposés en clair sur ton disque ou dans tes logs.

## 1. Principes
- **Zéro-Leak** : Pas de stockage de clés en clair.
- **AES-256** : Standard de chiffrement militaire.
- **Local-Only** : La clé maître reste sur ta machine, jamais exportée.

## 2. Usage
```python
# Chiffrer un secret
python .agent/skills/security-vault/scripts/vault.py encrypt "ma-super-cle-api"
```
