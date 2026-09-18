# RAPPORT — Mojo 1.0 face à la stack Vagus OS
**Étude technique + cartographie des processus + gains potentiels + feuille de route**

Date : 06/09/2026 — Rédigé par Hermes (Vagus OS), audit mesuré sur le VPS (135.125.53.215), sources web vérifiées (07/09 22h-23h CEST).

---

## 1. VERDICT EXÉCUTIF

**Mojo 1.0 est réel, mûr techniquement et désormais open source (Apache 2.0) — mais sur notre infrastructure mesurée, il ne fait gagner ni temps, ni efficacité, ni stockage à court terme.**

Les faits qui tranchent, mesurés ce soir :
- **Pas de GPU** (VGA virtio) : le terrain n°1 de Mojo/MAX (kernels GPU, inference accélérée) est hors sol.
- **CPU inactif** : load 0.39 sur 6 cœurs. Tous nos crons s'exécutent en <80 s, la plupart en <1 s.
- **Le code chaud est déjà natif** : llama.cpp (C++), ffmpeg, sqlite, tesseract, pymupdf, weasyprint. Mojo n'accélère pas ce qui est déjà compilé.
- **Le vrai goulot est ailleurs** : API LLM (réseau), RAM saturée (11 G dont 6,4 G utilisés, swap 2 G plein), stockage (61 G/99 G, dont ~10 G de caches purgables).

**Recommandation : ne pas porter de code en Mojo maintenant. Traiter d'abord la dette réelle (RAM + stockage, ~2 G RAM et 10-15 G récupérables sans Mojo). Réévaluer dans 6-12 mois** (maturité 1.x, stratégie Qualcomm, éventuel GPU).

---

## 2. MOJO 1.0 — ÉTAT DES LIEUX FACTUEL (sources vérifiées)

### 2.1 Ce que c'est
Langage **systèmes** à syntaxe Python, typage statique inféré + borrow checker (inspiration Rust), compilé via **MLIR/LLVM**, capable de cibler CPU, GPU, TPU et ASIC. Créé par Chris Lattner (créateur de LLVM, Clang et Swift) chez **Modular**, société **acquise par Qualcomm en juin 2026**.

### 2.2 Chronologie décisive
| Date | Événement |
|---|---|
| 2023 | Premières versions publiques (playground puis SDK Linux/macOS) |
| 03/2024 | Standard library open source (Apache 2.0) |
| 12/2025 | Roadmap officielle vers 1.0 |
| 07/05/2026 | Mojo 1.0.0 beta 1 + lancement de mojolang.org |
| **11/08/2026** | **Mojo 1.0.0 final** (release Modular 26.5) |
| **18/08/2026** | **Compilateur open source, licence Apache 2.0 + LLVM Exceptions** |
| 06/2026 | Acquisition de Modular par Qualcomm (annoncée juin, effective avant août) |

Communauté : ~200 contributeurs, 1 100+ PR fusionnées, 200 000+ lignes sur la stdlib.

### 2.3 Performances — ce que disent les mesures indépendantes
- **Étude Oak Ridge National Lab (SC25, arXiv 2509.21039)** — la référence académique : les kernels GPU Mojo sont **compétitifs avec CUDA et HIP sur les workloads memory-bound** (BabelStream, stencil 7 points) ; **des écarts subsistent en compute-bound fast-math et sur les opérations atomiques** (surtout AMD).
- **CPU vs CPython** : ordres de grandeur publiés de **10-100×** sur des boucles numériques pures (benchmark indépendant 03/2026 : 78-119× sur calcul numérique). Les chiffres marketing « 35 000× » de Modular datent de 2023 et portent sur des micro-kernels SIMD non représentatifs.
- **À relativiser** : sur de l'I/O, du parsing ou de l'orchestration (notre cas), l'écart avec Python tombe à 1-3×, voire nul.

### 2.4 Interopération Python — la limite structurelle
- Peut **importer des modules Python** via le runtime CPython (avec coût de franchissement de frontière).
- Peut être **appelé depuis Python** via des bindings C.
- **MAIS** : l'objectif « superset de Python » a été **abandonné en mars 2026**. Pas de classes Python (structs à la place), pas de compatibilité source. Un portage n'est pas une migration, c'est une réécriture.

### 2.5 Écosystème et outillage
- Installation : `uv pip install mojo` / `uv pip install max[all]` (le paquet historique `modular` est retiré en 26.6).
- **MAX** : framework d'inférence de Modular (serveurs dédiés, modèles GLM-5.2, Nemotron-H, Kimi 2.5…).
- **« Mojo AI Skills »** : skills agents officiels pour développer en Mojo/MAX (7 200+ téléchargements via skills.sh) — ce sont des aides au développement, pas des composants d'exécution.
- Feuille de route 1.x : modèle asynchrone robuste, pattern matching, unions — **pas encore là**.

### 2.6 Risques identifiés
1. **Qualcomm** : l'acquisition (juin 2026) crée une incertitude stratégique — atténuée par l'open source Apache 2.0 du compilateur, mais la gouvernance et la feuille de route restent pilotées par un grand groupe.
2. **Jeunesse** : 1.0 a 3 semaines en open source. Pas d'async mature, écosystème de packages très inférieur à Python.
3. **Coût de portage réel** : réécriture, pas traduction.

---

## 3. CARTOGRAPHIE DES PROCESSUS VAGUS OS (mesures du 06/09/2026)

### 3.0 Infrastructure
| Ressource | État mesuré |
|---|---|
| CPU | 6 vCPU virtio, **load 0.39** (quasi inactif) |
| RAM | 11 G — 6,4 G utilisés, **swap 2 G/2 G saturé** (contention mémoire) |
| Disque | 99 G — **61 G utilisés (65 %)**, 34 G libres |
| GPU | **Aucun** (VGA virtio Red Hat) |
| OS | Debian 12, Europe/Paris |

### 3.1 Orchestration planifiée (28 crons Hermes — tous mesurés)
| Famille | Exemples | Fréquence | Durée mesurée | Charge dominante |
|---|---|---|---|---|
| Scripts no_agent légers | healthcheck, watch-slmlocal, verify-greffier, collision-detector, db-maintenance, backups… | 30 min → 1/sem | **< 1 s** | I/O mineur |
| Script no_agent actif | transcripts-pulse | toutes les 15 min | **5 s** (96×/j = 8 min CPU/j) | I/O + parsing |
| Jobs agents LLM | dogma-breaker (76 s), twinvault (53 s), rapport quotidien, argos-watchman, omp-eval, synthèse hebdo | 1/j → 1/sem | 50-80 s | **100 % API LLM (réseau)** |
| Jobs mensuels | CCC meta-learning, nettoyages | 1/mois | < 1 s | I/O |

**Lecture ARGOS : 99,9 % du temps d'exécution planifié est du réseau (appels LLM) ou de l'attente I/O. Zéro boucle de calcul CPU significative.**

### 3.2 Services persistants (consommateurs mémoire)
| Service | Rôle | Poids RAM approx. |
|---|---|---|
| Hermes gateway + dashboard + webui | Cœur agentique | ~550 M |
| headroom (proxy fallback) + child | Routage LLM | ~850 M |
| llama-server (draft 1.5B) + embeddings | SLM local (C++ natif) | ~250 M |
| PRISM + proxies (8650/8790/8789…) | Couche locale | léger |
| **Elasticsearch (Docker)** | Index temporal | **~780 M** |
| **Temporal server + admin (Docker)** | Workflows | **~500 M** |
| Chromium headless résiduel | Browser | ~360 M |
| ~17 autres conteneurs Docker | kleia, transparence-citoyenne, n8n, vaultwarden, postiz, LOF… | ~1,5 G cumulé |

**Lecture : la RAM (11 G) est le vrai goulot matériel — le swap plein le confirme. Elasticsearch + Temporal + Chromium ≈ 1,6 G quasi inertes.**

### 3.3 Code maison (inventaire)
| Zone | Volume | Nature |
|---|---|---|
| Skills Vagus | **129 skills** (57 M avec références) | Markdown + scripts courts |
| Scripts cron du profil | 25 fichiers, ~3 KLoC | Shell + Python léger (orchestration) |
| Moteur CUSTOS + générateurs de thèmes | ~6 KLoC | Gematria (calculs µs), orchestration LLM, HTML/PDF |
| antigravity-brain (src + scripts) | ~17 KLoC | Orchestration, protocoles, kernel Rust expérimental |
| vagus_os (prototype gateway) | ~3 KLoC | Prototype (remplacé par Hermes) |
| Vagus Quant | engine.py (16 K) + pulse.py | Calculs financiers légers, 1×/sem |
| hermes-cortex (concepts/règles/RAG) | 24 concepts, 9 règles, index SQLite | Connaissance, indexation **1,2 s** |

**Total : ~30 KLoC Python effectif, dont ~0 % de code CPU-bound.** Le seul composant déjà « systèmes » de la stack est le kernel Rust expérimental d'antigravity (Rust, pas Mojo).

### 3.4 Stockage — où sont les 61 G
| Poste | Taille | Nature |
|---|---|---|
| **~/.cache** | **7,1 G** | huggingface 2,6 G (modèles téléchargés), puccinialin 2,0 G, puppeteer 643 M + playwright 641 M, uv 516 M, pip 276 M, chroma 167 M |
| ~/.hermes/hermes-agent | 2,9 G | Code source + venv Hermes (outil lui-même) |
| ~/.hermes/profiles | 1,3 G | Profils, logs, cron (executions.db…) |
| ~/.local/lib + bin + share | ~1,8 G | Paquets Python système, node_modules |
| Modèles | ~1,2 G | qwen2.5-coder 1,1 G, sherpa-onnx 758 M, nomic-embed 81 M |
| Venvs spécialisés | ~1,7 G | transcribe 620 M, prism 428 M, rag-env 424 M, venv-pdf 169 M, weasyprint 93 M |
| ~/workspace | 3,6 G | LOF 813 M, kleia 725 M, custos 582 M, site kleia-up 353 M, BSP JPL 132 M… |
| ~/transcripts | 806 M | Corpus audio/vidéo |
| ~/backups + .hermes/backups | ~340 M | Sauvegardes |
| Divers | ~1,5 G | vagus_os/gateway 462 M (prototype+venv), antigravity 404 M, PDCA 255 M, hermes-webui 222 M, .npm 400 M… |

### 3.5 Inférence locale
- Draft : **llama.cpp** (C++ natif) servant qwen2.5-coder-1.5B q4 (1,1 G) sur :11434 via ollama-like + llama-server 18080.
- Embeddings : nomic-embed via llama-server 18080.
- STT : sherpa-onnx (C++ natif).
- **Aucun de ces composants n'est en Python pur. Mojo n'aurait rien à accélérer ici.**

---

## 4. MATRICE DE PERTINENCE — MOJO vs NOS PROCESSUS

| Processus / composant | Charge dominante | Déjà natif ? | Gain Mojo estimé | Verdict |
|---|---|---|---|---|
| Indexation RAG (1,2 s/j) | I/O sqlite | sqlite natif | nul | 🔴 Non pertinent |
| 22 crons scripts (< 1-5 s) | I/O + shell | — | nul (déjà < 1 s) | 🔴 Non pertinent |
| 6 jobs agents (50-80 s) | **API LLM réseau** | — | nul (le CPU n'est jamais le facteur) | 🔴 Non pertinent |
| Inférence draft/embeddings | Inférence CPU | llama.cpp C++ | nul* (*MAX ne brille que sur GPU) | 🔴 Non pertinent |
| Parsing PDF / OCR / audio | Libs C/C++ | pymupdf, tesseract, ffmpeg, sherpa | nul | 🔴 Non pertinent |
| Moteur CUSTOS (gematria) | Micro-calculs | — | nul (µs en Python) | 🔴 Non pertinent |
| Génération HTML/PDF (thèmes, rapports) | WeasyPrint (C) + LLM | C | nul | 🔴 Non pertinent |
| Vagus Quant (1×/sem) | Calculs légers | — | nul (job < 1 s) | 🔴 Non pertinent |
| Prototype gateway vagus_os | I/O | — | nul (abandonné) | 🔴 Non pertinent |
| **Futur besoin GPU** (inférence locale plus grosse, kernels custom) | Calcul GPU | — | **réel (MAX, compétitif CUDA en memory-bound)** | 🟡 Option future |
| **Outils autonomes à distribuer** (binaires clients) | Divers | — | réel mais aucun besoin actuel | 🟡 Option future |

### Contre-argumentation structurée (rôle ARGOS)
1. **Le terrain n°1 de Mojo est hors sol** : pas de GPU sur ce VPS. MAX, kernels GPU, portabilité CUDA→ROCm : tout cela ne nous concerne pas aujourd'hui.
2. **Le CPU est inactif** : même un gain de 100× sur du calcul ne se verrait pas — rien ne calcule assez longtemps pour que ce soit mesurable.
3. **Notre code chaud est déjà compilé** : llama.cpp, ffmpeg, sqlite, tesseract, pymupdf, weasyprint, sherpa-onnx, redis, postgres. Le « gâteau » Python restant est de l'orchestration I/O-bound, exactement ce que Python fait bien et où Mojo ne gagne presque rien.
4. **Le coût réel dominant est l'API LLM** (latence + €) : le levier d'efficacité n'est pas un langage plus rapide, c'est le routage PRISM / draft local (déjà en place) et la frugalité des prompts.
5. **Le portage coûterait cher pour un gain nul** : ~30 KLoC d'orchestration + 129 skills liés à l'écosystème Python. Mojo n'est pas un superset Python (abandonné 03/2026) : ce serait une réécriture, pas une migration, avec un écosystème de packages immature et pas d'async avant 1.x.
6. **Risque plateforme** : Modular est détenu par Qualcomm depuis juin 2026. L'open source Apache 2.0 (18/08/26) sécurise le code, pas la direction du projet.

### Les vrais gisements révélés par l'audit (sans Mojo)
| Gisement | Gain estimé | Effort |
|---|---|---|
| Purge ~/.cache (huggingface 2,6 G, puccinialin 2 G, puppeteer/playwright 1,3 G, uv/pip ~0,8 G) | **6-7 G** | 30 min (vérifier puccinialin avant purge) |
| Élagage venvs/prototypes morts (vagus_os/gateway 462 M, venvs non référencés) | **1-3 G** | 30 min |
| BSP JPL non utilisés (de440 115 M + de421 17 M) si custos n'en a plus besoin | 130 M | 5 min |
| Réduire Elasticsearch + Temporal (1,3 G RAM) si transparence-citoyenne le permet | **~1,3 G RAM** | 1-2 h (étude impact) |
| Chromium headless résiduel (~360 M) : tuer le process orphelin | 360 M RAM | 1 min |
| Swap saturé → dégonfler après libération RAM | stabilité | automatique |
| **Total** | **~10-15 G disque, ~2 G RAM** | **une session** |

---

## 5. FEUILLE DE ROUTE

**Horizon T0 — cette semaine (sans Mojo, ~2-3 h)** : exécuter le plan de récupération ci-dessus (purge caches, élagage venvs/prototypes, kill chromium orphelin, décision Elasticsearch/Temporal). Gain : ~10-15 G disque, ~2 G RAM, fin du swap saturé. *Rapport ARGOS de fin de session avec les chiffres avant/après.*

**Horizon T1 — optionnel (si JP veut explorer Mojo concrètement, ~1/2 journée)** : POC sur le seul cas où Mojo pourrait un jour compter : compiler en binaire autonome un futur outil de traitement de corpus massif (ex. ré-indexation des 806 M de transcripts) — **uniquement si** un besoin de parsing/calcul intensif émerge. Verdict attendu du POC : confirmer que le goulot reste l'I/O disque. **Non recommandé aujourd'hui.**

**Horizon T2 — veille active (6-12 mois, coût zéro)** :
- Surveiller Mojo 1.x : modèle async, pattern matching, croissance de l'écosystème, signaux d'adoption (MAX, Qualcomm).
- Re-évaluer **MAX vs llama.cpp** le jour où une carte GPU arrive sur l'infra (MAX sert aujourd'hui GLM-5.2, Nemotron-H, Kimi 2.5 et revendique de meilleurs coûts d'inférence).
- Condition de réévaluation explicite : **(a)** GPU disponible, **(b)** besoin de kernels custom ou d'un outil autonome distribué, **(c)** apparition d'un script maison CPU-bound > 30 % d'un job quotidien. Aucune de ces conditions n'est remplie aujourd'hui.

---

## 6. RECOMMANDATION FINALE

**Verdict : Mojo 1.0 = excellente technologie, mauvaise réponse à notre problème actuel.** Notre système nerveux n'a pas besoin d'un langage plus rapide — il a besoin de moins de RAM, de moins de stockage mort et d'un routage LLM frugal. Le coût d'option de Mojo est nul (open source Apache 2.0) : on peut se permettre d'attendre la maturité 1.x sans rien perdre.

**Dette signalée (H8)** : le texte d'introduction fourni ce soir (réponse générique « Mojo peut aider Hermes/OMP ») contient des affirmations non vérifiées et des liens suspects (issue GitHub #77367 inexistante) — le présent rapport remplace cette analyse par des faits sourcés.

---

## SOURCES (vérifiées le 06/09/2026)
1. Blog officiel Modular — « Modular 26.5: Mojo 1.0 is here! » (11/08/2026)
2. The Register — « Modular's Mojo hits 1.0 milestone » (12/08/2026)
3. Wikipedia — Mojo (programming language) (état 09/2026)
4. Oak Ridge National Lab / SC25 WACCPD — arXiv:2509.21039
5. GitHub API — modular/modular (29,5 K★, actif), modular/skills
6. Roadmap officielle Mojo — docs.modular.com/mojo/roadmap
7. Mesures locales : executions.db (crons), ps/ss/free/df, du par répertoire, chronométrage RAG (06/09/2026 22h30-23h30 CEST)
