#!/usr/bin/env python3
"""Outil de la couche « sujets » (notebook Hermes).

Sous-commandes :
  dashboard             Génère sujets/DASHBOARD.md (carte globale, idempotent :
                        n'écrit que si le contenu change -> pas de boucle watcher).
  lier <slug> <session_id> "<apport>"
                        Rattache une session (conversation) a un sujet — rituel H1
                        de fin de session. Idempotent, 1 session = 1 seul sujet.
  non-liees [N]         Sessions recentes sans sujet (filet de securite hebdo).
  check "<titre>"       Anti-doublon : interroge le RAG et affiche les sujets
                        dont un contenu est proche. À LANCER AVANT toute création
                        de sujet.
  list                  Liste brute des sujets (frontmatter).

Stdlib uniquement (aucune dépendance), exécutable avec le python système.
"""
import sys, re, subprocess, json, datetime
from pathlib import Path

SUJETS = Path(__file__).resolve().parent
BUNDLE = SUJETS.parent
VENV_PY = BUNDLE / 'rag-env' / 'bin' / 'python3'
RAG_QUERY = BUNDLE / 'rag-env' / 'rag_query.py'
DASH = SUJETS / 'DASHBOARD.md'
STALE_DAYS = 30


def parse_frontmatter(text):
    """Parse strict du frontmatter : `key: value` + listes `[a, b]`."""
    m = re.match(r'^---\n(.*?)\n---', text, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if not line or line.startswith((' ', '-')):
            continue
        if ':' not in line:
            continue
        k, v = line.split(':', 1)
        fm[k.strip()] = v.strip()
    return fm


def fm_list(v):
    return [x.strip() for x in v.strip('[]').split(',') if x.strip()]


def count_questions(text):
    """Nombre de items non cochés (- [ ]) sous '## Questions ouvertes'."""
    m = re.search(r'^## Questions ouvertes\n(.*?)(?=^## |\Z)', text, re.S | re.M)
    if not m:
        return 0, 0
    items = re.findall(r'^\s*- \[( |x)\]', m.group(1), re.M)
    return len(items), sum(1 for i in items if i != 'x')


def section_sessions(text):
    """Bloc '## Sessions liées' seul — la session peut être CITÉE dans la synthèse
    sans être rattachée : ne jamais tester le corps entier (piège du faux 'déjà liée')."""
    m = re.search(r'^## Sessions liées\n(.*?)(?=^## |\Z)', text, re.S | re.M)
    return m.group(1) if m else None


def count_sessions(text):
    """Lignes de tableau sous '## Sessions liées' = conversations rattachées."""
    sec = section_sessions(text)
    if sec is None:
        return 0
    return len([l for l in sec.splitlines()
                if l.startswith('|') and '---' not in l and not l.startswith('| Date')])


def load_sujets():
    out = []
    for idx in sorted(SUJETS.glob('*/index.md')):
        raw = idx.read_text('utf-8')
        fm = parse_frontmatter(raw)
        total, open_q = count_questions(raw)
        n_src = len(list((idx.parent / 'sources').glob('*.md')))
        n_sess = count_sessions(raw)
        statut = fm.get('statut', 'actif')
        upd = fm.get('updated_at', '????-??-??')
        try:
            age = (datetime.date.today() - datetime.date.fromisoformat(upd)).days
        except ValueError:
            age = -1
        stale = age > STALE_DAYS and statut != 'clos'
        out.append({
            'slug': idx.parent.name, 'titre': fm.get('titre', idx.parent.name),
            'statut': statut, 'updated_at': upd, 'age': age, 'stale': stale,
            'n_src': n_src, 'n_sess': n_sess, 'open_q': open_q, 'total_q': total,
            'tags': fm_list(fm.get('tags', '')),
        })
    return out


def dashboard():
    suj = load_sujets()
    today = datetime.date.today().isoformat()
    lines = [
        '# DASHBOARD — Carte globale des sujets',
        '',
        f'Généré le {today} par `sujets.py dashboard` — fichier DÉRIVÉ, ne pas éditer à la main.',
        f'Sujets : {len(suj)} | Stales (> {STALE_DAYS} j) : {sum(1 for s in suj if s["stale"])} '
        f'| Questions ouvertes : {sum(s["open_q"] for s in suj)}',
        '',
        '| Sujet | Statut | MàJ | Sources | Sessions | Q. ouvertes | Tags |',
        '|---|---|---|---|---|---|---|',
    ]
    for s in suj:
        flag = ' ⚠️ STALE' if s['stale'] else ''
        lines.append(
            f'| [{s["titre"]}]({s["slug"]}/index.md) | {s["statut"]}{flag} | '
            f'{s["updated_at"]} ({s["age"]} j) | {s["n_src"]} | {s["n_sess"]} | '
            f'{s["open_q"]}/{s["total_q"]} | {", ".join(s["tags"][:5])} |'
        )
    lines += ['', '## Points d’attention', '']
    alerts = [f'- **{s["titre"]}** : dernière mise à jour il y a {s["age"]} j (synthèse à revoir)'
              for s in suj if s['stale']]
    alerts += [f'- **{s["titre"]}** : {s["open_q"]} question(s) ouverte(s) — prioriser'
               for s in suj if s['open_q'] >= 3]
    lines += alerts or ['- Aucun — tout est à jour.']
    lines.append('')
    content = '\n'.join(lines)
    # Écrit seulement si changement : sinon le watcher boucle sur son propre fichier.
    if DASH.exists() and DASH.read_text('utf-8') == content:
        print('dashboard: inchangé')
        return 0
    DASH.write_text(content, 'utf-8')
    print(f'dashboard: écrit ({len(suj)} sujets)')
    return 0


def check(titre):
    """Anti-doublon : RAG + filtre sur les sujets existants."""
    py = str(VENV_PY) if VENV_PY.exists() else sys.executable
    if not RAG_QUERY.exists():
        print('ERREUR: rag_query.py introuvable')
        return 1
    res = subprocess.run([py, str(RAG_QUERY), titre], capture_output=True, text=True)
    try:
        # sortie attendue : JSON (parfois entêtée par des barres de progression)
        txt = res.stdout[res.stdout.index('['):]
        hits = json.loads(txt)
    except (ValueError, json.JSONDecodeError):
        print('ERREUR: sortie RAG illisible'); print(res.stdout[:500]); return 1
    print(f'Query: {titre}\n')
    if not hits:
        print('Aucun hit — sujet probablement neuf.')
        return 0
    seen = set()
    for h in hits[:5]:
        p = h.get('path', '?')
        sujet = 'sujets' in p
        mark = '← SUJET EXISTANT' if sujet else ''
        print(f'[{h.get("score", 0):.3f}] {p} {mark}')
        if sujet and p not in seen:
            seen.add(p)
    dup = [h for h in hits[:5] if 'sujets' in h.get('path', '') and h.get('score', 0) >= 0.70]
    if dup:
        print(f'\n⚠️  RISQUE DE DOUBLON : {len(dup)} sujet(s) proche(s) (score >= 0.70).')
        print('    -> Rattacher la source à l\'existant au lieu de créer un nouveau sujet.')
        return 2
    print('\nOK : pas de sujet proche au seuil 0.70.')
    return 0


def lier(slug, session_id, note):
    """Rattache une session à un sujet : ligne dans '## Sessions liées'.

    Anti-doublon : une session ne peut appartenir qu'à UN seul sujet.
    """
    idx = SUJETS / slug / 'index.md'
    if not idx.exists():
        print(f'ERREUR: sujet "{slug}" introuvable. Sujets: ' +
              ', '.join(d.name for d in sorted(SUJETS.iterdir()) if d.is_dir()))
        return 1
    # une session = un seul sujet (lecture de la SEULE section : un id cité
    # dans une synthèse n'est pas une liaison)
    for other in sorted(SUJETS.glob('*/index.md')):
        if other == idx:
            continue
        sec = section_sessions(other.read_text('utf-8'))
        if sec and session_id in sec:
            print(f'ERREUR: session {session_id} deja liee a "{other.parent.name}".')
            return 2
    text = idx.read_text('utf-8')
    sec = section_sessions(text)
    if sec is not None and session_id in sec:
        print(f'deja liee: {session_id} -> {slug} (idempotent)')
        return 0
    date = datetime.date.today().isoformat()
    row = f'| {date} | `{session_id}` | {note} |\n'
    if sec is not None:
        # append en fin de table (derniere ligne commencant par |)
        lines = text.splitlines(keepends=True)
        idx_lignes = [i for i, l in enumerate(lines) if l.startswith('|')]
        if idx_lignes:
            lines.insert(max(idx_lignes) + 1, row)
        else:
            pos = next(i for i, l in enumerate(lines) if l.startswith('## Sessions'))
            lines.insert(pos + 1, '\n| Date | Session | Apport |\n|---|---|---|\n' + row)
        text = ''.join(lines)
    else:
        sec_tbl = ('## Sessions liées\n\n| Date | Session | Apport |\n|---|---|---|\n'
                   + row + '\n')
        # insertion avant '## Questions ouvertes' ; sinon avant '## Décisions' ; sinon en fin
        ancre = '## Questions ouvertes' if '## Questions ouvertes' in text else (
            '## Décisions' if '## Décisions' in text else None)
        if ancre:
            text = text.replace(ancre, sec_tbl + ancre, 1)
        else:
            text = text.rstrip('\n') + '\n\n' + sec_tbl
    # bump updated_at
    text = re.sub(r'^updated_at: .*$', f'updated_at: {date}', text, count=1, flags=re.M)
    idx.write_text(text, 'utf-8')
    print(f'liee: {session_id} -> {slug}')
    dashboard()
    return 0


def non_liees(limit=25):
    """Sessions recentes sans sujet — filet de securite hebdomadaire."""
    import subprocess
    r = subprocess.run(['hermes', 'sessions', 'list', '--limit', str(limit)],
                       capture_output=True, text=True)
    known = set()
    for idx in SUJETS.glob('*/index.md'):
        known.update(re.findall(r'`([0-9a-z_]{6,})`', idx.read_text('utf-8')))
    out = []
    for line in r.stdout.splitlines()[2:]:
        if not line.strip() or '─' in line:
            continue
        sid = line.split()[-1]
        if sid not in known:
            out.append(line)
    print(f'{len(out)} session(s) non liee(s) sur les {limit} dernieres:')
    for l in out:
        print(' ', l)
    return 0


def main():
    args = sys.argv[1:]
    if not args or args[0] == 'dashboard':
        return dashboard()
    if args[0] == 'list':
        for s in load_sujets():
            print(f'{s["slug"]} | {s["statut"]} | {s["updated_at"]} | src={s["n_src"]} | q={s["open_q"]}')
        return 0
    if args[0] == 'check' and len(args) >= 2:
        return check(' '.join(args[1:]))
    if args[0] == 'lier' and len(args) >= 4:
        return lier(args[1], args[2], ' '.join(args[3:]))
    if args[0] == 'non-liees':
        return non_liees(int(args[1]) if len(args) > 1 else 25)
    print(__doc__)
    return 1


if __name__ == '__main__':
    sys.exit(main())
