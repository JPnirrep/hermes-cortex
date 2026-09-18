#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build-infra-graph.py — Inférence automatique du graphe de dépendances Vagus OS.

Objectif : permettre la prédiction des conséquences en chaîne d'une action
(suppression / modification / panne d'un nœud). Sans graphe, la réponse à
« qu'est-ce qui tombe si je supprime X ? » est « probablement rien ».

Sources d'inférence (toutes locales, lecture seule, coût zéro) :
  1. cron/jobs.json          → nœuds cron, scripts consommés, livraison
  2. scripts/                → nœuds script, fichiers/dossiers lus-écrits
  3. systemd (user + system) → nœuds service, ExecStart → script consommé
  4. .env                    → nœuds secret (clé logique uniquement), consommés par scripts
  5. docker ps               → nœuds conteneur, ports publiés
  6. ss -tlnp                → nœuds port, process propriétaire
  7. crontab -l              → nœuds cron système

Arêtes typées :
  depends_on | produces | consumes | delivers_to | listens_on | requires_secret
  | part_of | documents

Sortie :
  ~/hermes-cortex/knowledge/infra-graph.yaml   (graphe complet, source de vérité)
  + test de suppression : quels nœuds tombent si X disparaît (transitivité)

Usage :
  python3 build-infra-graph.py                # reconstruit le graphe
  python3 build-infra-graph.py --impact X     # test d'impact sur le nœud X
  python3 build-infra-graph.py --json         # sortie JSON (debug)

Auteur : Vagus OS / OPENCODE — 2026-09-13
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone

HOME = "/home/debian"
PROFILE = f"{HOME}/.hermes/profiles/vagus"
CORTEX = f"{HOME}/hermes-cortex"
OUT_YAML = f"{CORTEX}/knowledge/infra-graph.yaml"
OUT_JSON = f"{CORTEX}/knowledge/infra-graph.json"

# Nœuds ignorés : bruit système qui pollue le graphe sans valeur prédictive.
NOISE_PATHS = re.compile(
    r"/(proc|sys|dev|run|tmp|var/log|var/cache|var/lib/(dpkg|apt)|usr/(share|lib)|"
    r"etc/(ssl|cron\.d|systemd)|snap)/"
)
# Fichiers de données volumineux / artefacts dérivés : consommés mais non structurels.
DERIVED = re.compile(r"\.(log|db|sqlite|sqlite3|-wal|-shm|lock|pyc|bak)$|/sessions/|/cron/output/")

SECRET_RE = re.compile(r"\b([A-Z][A-Z0-9_]{2,}(?:_(?:API_)?(?:KEY|TOKEN|PASS|PASSWORD|SECRET|USER|ID)))\b|"
                       r"\b(EMAIL_JP|VAULT_TOKEN|LINKEDIN_[A-Z_]+)\b")

# Chemins de type "interpréteur / runtime" : ce ne sont pas des dépendances métier.
RUNTIME_PATH = re.compile(
    r"/bin/(python3?|python|node|bash|sh|php)$|/venv/bin/|python3$|"
    r"/(hermes-agent|transcribe-env)/"
)


def run(cmd, timeout=20):
    """Exécute une commande shell, retourne stdout (str) ou '' en cas d'échec."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except Exception:
        return ""


def nid(kind, name):
    """Identifiant de nœud stable et lisible : 'kind:name'."""
    return f"{kind}:{name}"


class Graph:
    def __init__(self):
        self.nodes = {}                        # id -> attributs
        self.edges = []                        # (src, rel, dst, meta)

    def node(self, kind, name, **attrs):
        k = nid(kind, name)
        cur = self.nodes.setdefault(k, {"id": k, "kind": kind, "name": name})
        cur.update({a: v for a, v in attrs.items() if v not in (None, "", [], {})})
        return k

    def edge(self, src, rel, dst, **meta):
        if src == dst:
            return
        for e in self.edges:
            if e[0] == src and e[1] == rel and e[2] == dst:
                return
        self.edges.append((src, rel, dst, meta))

    # ---------- inférence ----------

    def scan_scripts(self):
        """Nœuds script + fichiers/dossiers sys qu'ils lisent, + secrets référencés."""
        sdir = f"{PROFILE}/scripts"
        if not os.path.isdir(sdir):
            return
        for f in sorted(os.listdir(sdir)):
            p = os.path.join(sdir, f)
            if not os.path.isfile(p) or f.startswith("."):
                continue
            try:
                txt = open(p, errors="ignore").read()
            except Exception:
                continue
            exc = f.startswith(".")
            sk = self.node("script", f,
                           path=p,
                           executable=os.access(p, os.X_OK),
                           size=len(txt),
                           derived=bool(DERIVED.search(f)))
            # fichiers/dossiers sys référencés
            for m in set(re.findall(r"/home/debian/[A-Za-z0-9_./\-]+", txt)):
                m = m.rstrip(".,;:'\")")
                if NOISE_PATHS.search(m) or len(m) < 12:
                    continue
                if m.startswith(PROFILE + "/scripts"):
                    continue
                if RUNTIME_PATH.search(m):
                    continue
                # ne garder que les chemins qui ressemblent à une dépendance réelle
                if not re.search(r"\.(py|sh|yaml|yml|json|md|env|csv|txt|db|html)$|/[A-Za-z0-9_\-]+/?$", m):
                    continue
                kind = "file" if re.search(r"\.\w{1,5}$", m) else "dir"
                dk = self.node(kind, m, path=m)
                self.edge(sk, "consumes", dk)
            # secrets référencés (nom de variable seulement, JAMAIS la valeur)
            for grp in set(re.findall(SECRET_RE, txt)):
                groups = grp if isinstance(grp, tuple) else (grp,)
                for v in groups:
                    if v and re.match(r"^[A-Z][A-Z0-9_]{2,}$", v):
                        s = self.node("secret", v, storage=".env / Agent Vault")
                        self.edge(sk, "requires_secret", s)
            # services HTTP appelés (ports loopback)
            for port in set(re.findall(r"127(?:\.0)*\.0?1:(\d{2,5})", txt)):
                self.edge(sk, "consumes", self.node("port", port, address=f"127.0.0.1:{port}"))

    def scan_crons_hermes(self):
        p = f"{PROFILE}/cron/jobs.json"
        if not os.path.exists(p):
            return
        try:
            jobs = json.load(open(p)).get("jobs", [])
        except Exception:
            return
        dmap = {"local": "local", "origin": "origin", "telegram": "telegram"}
        for j in jobs:
            name = j.get("name") or j.get("id", "?")
            sched = j.get("schedule") or {}
            ck = self.node("cron", name,
                           job_id=j.get("id"),
                           schedule=sched.get("display") or sched.get("expr") or str(sched),
                           enabled=j.get("enabled", True),
                           no_agent=j.get("no_agent", False),
                           deliver=str(j.get("deliver")),
                           last_status=j.get("last_status"),
                           last_run_at=j.get("last_run_at"),
                           model=j.get("model"),
                           provider=j.get("provider"),
                           failure_streak=j.get("failure_streak") or 0)
            sc = j.get("script")
            if sc:
                s = self.node("script", os.path.basename(sc))
                self.edge(ck, "depends_on", s)
            d = str(j.get("deliver") or "")
            if d and d not in ("local", ""):
                dk = self.node("channel", d.split(":")[0])
                self.edge(ck, "delivers_to", dk)
            if j.get("last_delivery_error"):
                self.nodes[ck]["delivery_error"] = str(j["last_delivery_error"])[:200]
            # Dépendances implicites de provider : un job agent (no_agent=False) ou un job
            # pinné sur un modèle a besoin de la clé API du provider — même sans appel direct
            # dans un script. C'est le principal angle mort de l'inférence par script.
            prov = (j.get("provider") or "").lower()
            if prov and not j.get("no_agent"):
                secret = {"deepseek": "DEEPSEEK_API_KEY",
                          "inception": "INCEPTION_API_KEY",
                          "openai": "OPENAI_API_KEY",
                          "anthropic": "ANTHROPIC_API_KEY"}.get(prov)
                if secret:
                    self.edge(ck, "requires_secret",
                              self.node("secret", secret, storage=".env / Agent Vault"),
                              implicit=True)
            # Un job qui audite/vérifie d'autres jobs dépend d'eux en lecture
            if re.search(r"watchman|verif|greffier|health|detect", name, re.I):
                self.nodes[ck]["role"] = "audit"

    def scan_systemd(self):
        units = []
        for scope, cmd in (("user", "systemctl --user list-units --type=service --state=running --no-pager --plain"),
                           ("system", "systemctl list-units --type=service --state=running --no-pager --plain")):
            for line in run(cmd).splitlines():
                m = re.match(r"^\s*(\S+\.service)\s+loaded\s+active", line)
                if m:
                    units.append((scope, m.group(1)))
        for scope, u in units:
            base = u[:-len(".service")]
            try:
                txt = run(f"systemctl show -p ExecStart --value {u} 2>/dev/null || "
                          f"systemctl --user show -p ExecStart --value {u} 2>/dev/null").strip()
            except Exception:
                txt = "" if scope == "user" else run(f"systemctl show -p ExecStart --value {u}").strip()
            if not txt:
                txt = run(f"systemctl show -p ExecStart --value {u} 2>/dev/null").strip()
            if not txt:
                txt = run(f"systemctl --user show -p ExecStart --value {u} 2>/dev/null").strip()
            n = self.node("service", base, unit=u, scope=scope)
            for m in re.findall(r"/home/debian/[A-Za-z0-9_./\-]+", txt):
                m = m.strip()
                if m.endswith("/python3") or "/venv/bin/" in m:
                    continue
                if m.endswith(".py") or m.endswith(".sh"):
                    self.edge(n, "depends_on", self.node("script", os.path.basename(m), path=m))
                elif os.path.isdir(m):
                    self.edge(n, "part_of", self.node("dir", m, path=m))
            for port in set(re.findall(r"--port\s+(\d{2,5})", txt)):
                self.edge(n, "listens_on", self.node("port", port))

    def scan_ports(self):
        out = run("ss -tlnp 2>/dev/null")
        for line in out.splitlines():
            if "LISTEN" not in line:
                continue
            m = re.search(r"(\S+):(\d+)\s+\S+\s+\S+\s+(.*)", line)
            if not m:
                continue
            addr, port, rest = m.groups()
            p = self.node("port", port, address=f"{addr}:{port}")
            procs = re.findall(r'\("([^"]+)",pid=(\d+)', rest)
            for pname, pid in procs:
                s = self.node("process", pname, example_pid=pid)
                self.edge(s, "listens_on", p)

    def scan_docker(self):
        out = run("docker ps --format '{{.Names}}|{{.Image}}|{{.Ports}}' 2>/dev/null")
        for line in out.splitlines():
            parts = line.split("|")
            if len(parts) < 3:
                continue
            name, image, ports = parts[0], parts[1], parts[2]
            c = self.node("container", name, image=image, ports=ports or None)
            for m in re.findall(r"0\.0\.0\.0:(\d+)->", ports):
                self.edge(c, "listens_on", self.node("port", m, address=f"0.0.0.0:{m}"))

    def scan_crontab(self):
        out = run("crontab -l 2>/dev/null")
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^([\d*/,\- ]+)\s+(.*)$", line)
            if not m:
                continue
            sched, cmdline = m.group(1).strip(), m.group(2)
            scripts = re.findall(r"[A-Za-z0-9_./\-]+\.(?:sh|py)", cmdline)
            label = scripts[0] if scripts else cmdline[:40]
            c = self.node("cron_sys", label, schedule=sched, command=cmdline[:200])
            for sc in scripts:
                base = os.path.basename(sc)
                self.edge(c, "depends_on", self.node("script", base,
                          path=sc if sc.startswith("/") else None))

    def scan_env_secrets(self):
        """.env n'est jamais lu en valeur : seuls les NOMS de clés deviennent des nœuds
        s'ils sont déjà référencés par un script (sinon bruit)."""
        p = f"{PROFILE}/.env"
        if not os.path.exists(p):
            return
        try:
            names = set()
            for line in open(p, errors="ignore"):
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k = line.split("=", 1)[0].strip()
                    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k):
                        names.add(k)
        except Exception:
            return
        existing = {n["name"] for k, n in self.nodes.items() if n["kind"] == "secret"}
        for k in sorted(names & existing):
            self.nodes[nid("secret", k)]["present_in_env"] = True
        # Un nœud .env agrégé, sans valeurs
        e = self.node("file", f"{PROFILE}/.env", path=p, note="clés seulement, valeurs jamais lues")
        return e

    def scan_data_flows(self):
        """Complète l'inférence : un cron qui LIT un fichier de données n'a pas
        forcément le chemin en dur dans son script (le script le lit dans un
        dossier, ou le job agent le découvre à l'exécution). On croise donc :
          - le nom du job (normalisé) avec les fichiers de données portant son nom
          - les répertoires de données connus avec les scripts qui les consomment

        Sans cette passe, 75% du graphe est en nœuds feuilles et le test de
        suppression ne détecte presque rien."""
        for k, n in list(self.nodes.items()):
            if n["kind"] != "cron" or n.get("no_agent") is not True:
                continue
            name = n["name"]
            # 1. Fichiers de données portant le nom du job (normalisé)
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            slug2 = slug.replace("-", "_")
            for base in (f"{CORTEX}/knowledge", f"{CORTEX}/reports", f"{CORTEX}/metrics",
                         f"{HOME}/.hermes/profiles/vagus", f"{HOME}/workspace"):
                if not os.path.isdir(base):
                    continue
                try:
                    for f in os.listdir(base):
                        fl = f.lower()
                        if slug2 in fl.replace("-", "_") or slug in fl.replace("_", "-"):
                            fp = os.path.join(base, f)
                            if os.path.isfile(fp) and not f.endswith(".py"):
                                self.edge(k, "consumes", self.node("file", fp, path=fp),
                                          inferred=True)
                except Exception:
                    pass
            # 2. Répertoires de données consommés (depuis le script du job)
            sc = n.get("script")
            if sc:
                sid = nid("script", os.path.basename(sc))
                for e in self.edges:
                    if e[0] == sid and e[1] == "consumes":
                        # propager la consommation de données vers le cron
                        self.edge(k, "consumes", e[2], inferred=True)

    # ---------- analyse ----------

    def impact(self, target):
        """Test de suppression : quels nœuds deviennent inopérants si `target` disparaît.
        Transitivité sur les arêtes de dépendance entrantes."""
        # index inverse : dst -> [(src, rel)]
        rev = defaultdict(list)
        for s, rel, d, _ in self.edges:
            rev[d].append((s, rel))
        seen, frontier = set(), [target if ":" in target else None]
        if frontier[0] is None:
            cands = [k for k in self.nodes if k.endswith(":" + target) or self.nodes[k]["name"] == target]
            frontier = cands
        seen.update(frontier)
        affected = []
        while frontier:
            cur = frontier.pop()
            for src, rel in rev.get(cur, []):
                if src in seen:
                    continue
                if rel in ("depends_on", "requires_secret", "part_of", "delivers_to"):
                    seen.add(src)
                    affected.append((src, rel, cur))
                    frontier.append(src)
        return affected

    def stats(self):
        kinds = defaultdict(int)
        for n in self.nodes.values():
            kinds[n["kind"]] += 1
        rels = defaultdict(int)
        for *_, rel in [(e[0], e[1], e[2]) for e in self.edges]:
            rels[rel] += 1
        return dict(kinds), dict(rels)

    def critical_nodes(self):
        """Nœuds les plus 'critiques' = ceux dont la disparition impacte le plus de nœuds."""
        scored = []
        for k in self.nodes:
            n = len(self.impact(k))
            if n:
                scored.append((n, self.nodes[k]["kind"], self.nodes[k]["name"]))
        scored.sort(reverse=True)
        return scored

    # ---------- sérialisation ----------

    def to_dict(self):
        kinds, rels = self.stats()
        return {
            "meta": {
                "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                "generator": "build-infra-graph.py",
                "source": "inférence locale (cron/systemd/scripts/docker/ports/crontab)",
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "vault_scan": False,
                "kinds": kinds,
                "relations": rels,
            },
            "nodes": [
                self.nodes[k] for k in sorted(self.nodes)
            ],
            "edges": [
                {"from": s, "rel": rel, "to": d, **meta}
                for s, rel, d, meta in sorted(self.edges, key=lambda e: (e[0], e[1], e[2]))
            ],
        }


def yaml_dump(d):
    """Sérialiseur YAML minimal (pas de dépendance PyYAML dans le python système)."""
    try:
        import yaml
        return yaml.safe_dump(d, allow_unicode=True, sort_keys=False, default_flow_style=False, width=200)
    except ImportError:
        return json.dumps(d, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--impact", help="Nœud cible : affiche les nœuds impactés s'il disparaît")
    ap.add_argument("--json", action="store_true", help="Sortie JSON brute")
    ap.add_argument("--no-write", action="store_true", help="Ne pas écrire les fichiers")
    a = ap.parse_args()

    g = Graph()
    for step in ("scan_scripts", "scan_crons_hermes", "scan_systemd", "scan_ports",
                 "scan_docker", "scan_crontab", "scan_env_secrets", "scan_data_flows"):
        try:
            getattr(g, step)()
        except Exception as e:
            print(f"  [!] {step}: {e}", file=sys.stderr)

    if a.impact:
        res = g.impact(a.impact)
        print(f"IMPACT de la disparition de '{a.impact}' : {len(res)} nœud(s)")
        for src, rel, via in res:
            print(f"  {g.nodes[src]['kind']:<10} {g.nodes[src]['name']:<38} ({rel} → {via})")
        if not res:
            print("  aucun nœud dépendant (nœud feuille ou non indexé)")
        return

    d = g.to_dict()
    if a.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return

    kinds, rels = g.stats()
    print("=== GRAPHE D'INFRASTRUCTURE VAGUS OS ===")
    print(f"nœuds : {len(g.nodes)}   arêtes : {len(g.edges)}")
    print("types  :", ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    print("arêtes :", ", ".join(f"{k}={v}" for k, v in sorted(rels.items())))

    if not a.no_write:
        os.makedirs(os.path.dirname(OUT_YAML), exist_ok=True)
        with open(OUT_YAML, "w") as f:
            f.write("# Graphe de dépendances Vagus OS — généré automatiquement.\n"
                    "# NE PAS éditer à la main : lancer tools/build-infra-graph.py\n"
                    "# Test de validité : python3 build-infra-graph.py --impact <nœud>\n\n")
            f.write(yaml_dump(d))
        with open(OUT_JSON, "w") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print(f"écrit : {OUT_YAML}")
        print(f"écrit : {OUT_JSON}")


if __name__ == "__main__":
    main()
