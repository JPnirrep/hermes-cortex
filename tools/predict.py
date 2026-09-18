#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
predict.py — Journal de prédiction Vagus OS.

Mesure la fiabilité prédictive réelle de Vagus OS sur les conséquences de ses
actions. La prédiction est écrite AVANT de connaître le résultat : sans cette
contrainte, on réécrit l'histoire et la mesure ne vaut rien.

Usage :
  # 1. Avant d'agir — écrire la prédiction (obligatoire avant toute action non triviale)
  python3 predict.py predict \
      --action "Supprimer le cron Healthcheck VPS" \
      --expected "Le healthcheck horaire disparaît, aucune alerte de panne" \
      --impacts "cron:Healthcheck VPS" \
      --confidence 0.85

  # 2. Après avoir vérifié l'état réel — consigner l'observation
  python3 predict.py observe --id 20260913-2201-01 \
      --actual "Confirmé : plus de run depuis la suppression" \
      --class exact

  # 3. KPIs
  python3 predict.py kpi
  python3 predict.py list [--open]
  python3 predict.py due           # prédictions ouvertes à vérifier (J+1 et plus)

Classes d'écart : exact | partial | wrong | surprise

Auteur : Vagus OS / OPENCODE — 2026-09-13
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from statistics import mean

HOME = "/home/debian"
CORTEX = f"{HOME}/hermes-cortex"
JOURNAL = f"{CORTEX}/knowledge/prediction-journal.jsonl"
GRAPH = f"{CORTEX}/knowledge/infra-graph.json"
CLASSES = ("exact", "partial", "wrong", "surprise")


def now():
    return datetime.now().astimezone()


def load_journal():
    if not os.path.exists(JOURNAL):
        return []
    out = []
    for line in open(JOURNAL, errors="ignore"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def append_entry(e):
    os.makedirs(os.path.dirname(JOURNAL), exist_ok=True)
    with open(JOURNAL, "a") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")


def rewrite(entries):
    """Réécrit le journal (les entrées 'observe' sont des mises à jour, pas des ajouts)."""
    with open(JOURNAL, "w") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def next_id():
    d = now().strftime("%Y%m%d-%H%M")
    n = 1
    existing = {e.get("id") for e in load_journal()}
    while f"{d}-{n:02d}" in existing:
        n += 1
    return f"{d}-{n:02d}"


def graph_lookup(target):
    """Interroge le graphe pour les impacts réels d'un nœud — sert à vérifier
    si la prédiction d'impacts était couvrante."""
    if not os.path.exists(GRAPH):
        return None
    try:
        g = json.load(open(GRAPH))
    except Exception:
        return None
    nodes = {n["id"]: n for n in g["nodes"]}
    key = target if target in nodes else None
    if key is None:
        for k, n in nodes.items():
            if n["name"] == target or k.endswith(":" + target):
                key = k
                break
    if key is None:
        return None
    rev = {}
    for e in g["edges"]:
        rev.setdefault(e["to"], []).append((e["from"], e["rel"]))
    seen, frontier, found = {key}, [key], []
    while frontier:
        cur = frontier.pop()
        for src, rel in rev.get(cur, []):
            if src in seen or rel not in ("depends_on", "requires_secret", "part_of"):
                continue
            seen.add(src)
            found.append(src)
            frontier.append(src)
    return found


# ---------------- commandes ----------------

def cmd_predict(a):
    e = {
        "id": next_id(),
        "created_at": now().isoformat(timespec="seconds"),
        "status": "open",
        "action": a.action,
        "prediction": {
            "expected": a.expected,
            "impacts": [x.strip() for x in (a.impacts or "").split(",") if x.strip()],
            "confidence": a.confidence,
            "reversible": a.reversible,
        },
        "observation": None,
        "delta": None,
    }
    append_entry(e)
    # enrichissement : le graphe connaît-il des impacts que je n'ai pas prédits ?
    hints = []
    for t in e["prediction"]["impacts"]:
        found = graph_lookup(t)
        if found:
            hints += [x for x in found if x not in e["prediction"]["impacts"]]
    print(f"PREDICTION {e['id']} enregistrée (confiance {a.confidence})")
    print(f"  action    : {a.action}")
    print(f"  attendu   : {a.expected}")
    if hints:
        print(f"  ⚠ graphe : {len(set(hints))} nœud(s) dépendant(s) NON prédits →")
        for h in sorted(set(hints))[:12]:
            print(f"      {h}")
        print("  → inclure ces nœuds dans la prédiction ou justifier l'écart")
    return e["id"]


def cmd_observe(a):
    entries = load_journal()
    target = None
    for e in entries:
        if e.get("id") == a.id:
            target = e
            break
    if target is None:
        print(f"ERREUR: prédiction {a.id} introuvable")
        sys.exit(1)
    if a.class_ not in CLASSES:
        print(f"ERREUR: classe invalide '{a.class_}'. Attendu : {', '.join(CLASSES)}")
        sys.exit(1)
    target["observation"] = {
        "actual": a.actual,
        "verified_at": now().isoformat(timespec="seconds"),
        "class": a.class_,
        "note": a.note or "",
    }
    target["status"] = "closed"
    target["delta"] = {
        "predicted_confidence": target["prediction"]["confidence"],
        "class": a.class_,
        "missed_impacts": [x.strip() for x in (a.missed or "").split(",") if x.strip()],
    }
    rewrite(entries)
    print(f"PREDICTION {a.id} fermée — écart : {a.class_}")
    if a.class_ in ("wrong", "surprise") and not (a.note or ""):
        print("  ⚠ écart majeur sans note : documenter la cause (règle anti-récurrence)")
    return target


def compute_kpis(entries):
    closed = [e for e in entries if e.get("status") == "closed" and e.get("delta")]
    open_ = [e for e in entries if e.get("status") == "open"]
    if not closed:
        return {"total": len(entries), "closed": 0, "open": len(open_), "kpi": None}
    cls = [e["delta"]["class"] for e in closed]
    n = len(closed)
    exact = cls.count("exact")
    partial = cls.count("partial")
    wrong = cls.count("wrong")
    surprise = cls.count("surprise")
    accuracy = (exact + partial) / n
    conf = mean(e["delta"]["predicted_confidence"] for e in closed)
    with_g = [e for e in closed if e["delta"].get("missed_impacts")]
    return {
        "total": len(entries),
        "closed": n,
        "open": len(open_),
        "kpi": {
            "accuracy": round(accuracy, 3),
            "exact": exact, "partial": partial, "wrong": wrong, "surprise": surprise,
            "surprise_rate": round(surprise / n, 3),
            "confidence_mean": round(conf, 3),
            "calibration_bias": round(conf - accuracy, 3),
            "graph_coverage": round(1 - len(with_g) / n, 3),
            "median_age_days": round(mean([
                (datetime.fromisoformat(e["observation"]["verified_at"]) -
                 datetime.fromisoformat(e["created_at"])).total_seconds() / 86400
                for e in closed]), 1),
        },
    }


def cmd_kpi(a):
    e = load_journal()
    r = compute_kpis(e)
    print("=== KPI JOURNAL DE PRÉDICTION ===")
    print(f"prédictions : {r['total']}  (fermées {r['closed']}, ouvertes {r['open']})")
    if not r["kpi"]:
        print("aucune prédiction fermée — pas de KPI calculable")
        return
    k = r["kpi"]
    print(f"taux de justesse     : {k['accuracy']*100:.1f}%   (exact {k['exact']} / partial {k['partial']} / wrong {k['wrong']} / surprise {k['surprise']})")
    print(f"taux de surprise     : {k['surprise_rate']*100:.1f}%   ← trous du modèle du monde")
    print(f"confiance moyenne    : {k['confidence_mean']*100:.1f}%")
    b = k["calibration_bias"]
    verdict = "surconfiance" if b > 0.05 else ("sous-confiance" if b < -0.05 else "calibré")
    print(f"biais de calibration : {b*100:+.1f} pts  → {verdict}")
    print(f"couverture du graphe : {k['graph_coverage']*100:.1f}%")
    print(f"délai moyen vérif.   : {k['median_age_days']} j")
    if k["surprise_rate"] > 0.2:
        print("⚠ taux de surprise > 20% : le modèle du monde a des trous structurels —")
        print("  chaque surprise doit produire une règle anti-récurrence (règle H8).")


def cmd_list(a):
    e = load_journal()
    if a.open:
        e = [x for x in e if x.get("status") == "open"]
    if not e:
        print("journal vide" if not a.open else "aucune prédiction ouverte")
        return
    for x in e:
        st = x.get("status")
        cl = (x.get("delta") or {}).get("class", "-")
        c = x["prediction"]["confidence"]
        print(f"{x['id']}  {st:<6} {cl:<8} conf={c}  {x['action'][:66]}")


def cmd_due(a):
    """Prédictions ouvertes depuis plus de 24 h : à vérifier, boucle fermée."""
    e = load_journal()
    cutoff = now() - timedelta(hours=24)
    due = [x for x in e if x.get("status") == "open"
           and datetime.fromisoformat(x["created_at"]) < cutoff]
    if not due:
        print("aucune prédiction en retard de vérification")
        return
    print(f"{len(due)} prédiction(s) ouverte(s) > 24 h à vérifier :")
    for x in due:
        age = (now() - datetime.fromisoformat(x["created_at"])).days
        print(f"  {x['id']}  J+{age}  {x['action'][:70]}")
        print(f"      attendu : {x['prediction']['expected'][:100]}")


def main():
    ap = argparse.ArgumentParser(description="Journal de prédiction Vagus OS")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("predict", help="écrire une prédiction AVANT d'agir")
    p.add_argument("--action", required=True)
    p.add_argument("--expected", required=True)
    p.add_argument("--impacts", default="")
    p.add_argument("--confidence", type=float, required=True)
    p.add_argument("--reversible", default="unknown", choices=["yes", "no", "unknown"])
    p.set_defaults(func=cmd_predict)

    o = sub.add_parser("observe", help="consigner l'observation après vérification")
    o.add_argument("--id", required=True)
    o.add_argument("--actual", required=True)
    o.add_argument("--class", dest="class_", required=True)
    o.add_argument("--missed", default="")
    o.add_argument("--note", default="")
    o.set_defaults(func=cmd_observe)

    k = sub.add_parser("kpi", help="afficher les KPI")
    k.set_defaults(func=cmd_kpi)

    l = sub.add_parser("list", help="lister les prédictions")
    l.add_argument("--open", action="store_true")
    l.set_defaults(func=cmd_list)

    d = sub.add_parser("due", help="prédictions en retard de vérification")
    d.set_defaults(func=cmd_due)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
