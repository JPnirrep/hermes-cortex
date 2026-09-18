---
type: concept
name: vigie-sante
timestamp: 2026-08-30
tags: [vigie, sante, chirurgien, ia-souveraine, business-plan, orchestration]
links:
  - concepts/entreprise-autonome
  - concepts/plaquette-kleia-up
  - concepts/vagus-kg-v2.1
---

# VIGIE Santé — « l'OS du chirurgien libéral »

Projet commercial : orchestration IA souveraine à coût quasi zéro pour chirurgiens libéraux français. Vendu sur la PROTECTION du praticien (pas le ROI gadget) : conformité, preuve, temps récupéré.

## Produit
- **3 phases, prix fixes** (garde-fou : jamais « sur devis » pour l'essentiel) : Audit-Vigie 4 900 € (7 j) · Architecture de repli 12 900 € (2-4 sem) · Vigie continue 1 190 €/mois (12 mois)
- Architecture : code 70 % → workflows (n8n ou Langflow/Windmill) 25 % → agentique LLM 5 % (le LLM ne décide jamais, il reformule)
- Le Concile = différenciateur : garde-fous empilés (déterminisme, A.V.E.C., pseudonymisation, piste d'audit signée cosign/Rekor, multi-provider, prix fixes, boucles fermées, escalade humaine)
- Cible : ~3 000 chirurgiens libéraux FR ; transposable aux professions réglementées (avocats, experts-comptables, architectes)

## Stack open-source (scan GitHub 30/08/2026, 22 repos vérifiés API)
- 🟢 12 repos permissifs : Ollama, llama.cpp, RAGFlow (citations sourcées), Qdrant, txtai, Presidio (pseudonymisation), whisper.cpp, cosign+Rekor, OTel Collector, Langflow (MIT), Node-RED, mustangproject (Factur-X)
- 🟡 à trancher : **licence n8n (fair-code)** — si refus juridique → Langflow/Windmill. Dify/Activepieces/Flowise/Twenty/ERPNext/InvoiceNinja en NOASSERTION/AGPL
- GRAD-RAG : aucune implémentation maintenue → grounding couvert par RAGFlow

## Marché (sources 30/08/2026)
- Case vide : aucun acteur ne combine orchestration multi-LLM + audit conformité + veille + preuve signée
- Proche FR : Nabla 69 €/mois (outil seul), Dragon 53 €/mois, MIA Chirurgie (seul natif IA cible, HDS, outil métier pas gouvernance), Cyberclair audit 390-690 € (scan OSINT seul), Doctolib ~135 €/mois, secrétaire médicale ~3 500 €/mois
- Lointain : DAX 369 $/mois + 700 $ setup (page pricing = gabarit à copier), Suki 299-399 $, Ambience 2 800-5 000 $/an, Harvey 1 000-2 000 $/siège (pilote → scale), CPA Pilot 89 $/mois (« audit defense »), Corti (narratif souveraineté UE)
- Prix VIGIE 10× sous DAX pour un OS complet → argument disruptif, pas un problème

## Fichiers clés
- ~/workspace/vigie-sante-vision-commerciale.md — vision (4 tueurs, Concile, 3 phases)
- ~/workspace/vigie-sante-sourcing-benchmark-2026-08-30.md — scan GitHub + benchmark offres
- ~/workspace/vigie-sante/pricing-vigie.html + .pdf — maquette page tarifs DAX-style
- ~/workspace/vigie-sante-etude-marche-2026-08-31.md — rapport mission nocturne (TAM/SAM/SOM)
- ~/workspace/vigie-sante/livraison/ — étude consolidée + business plan (HTML/PDF, envoi mail 31/08 08h00)

## Prochaines décisions
1. Licence n8n → valider ou basculer (Langflow MIT)
2. Premier client = prototype neurochirurgien (règle d'or)
3. Contrat type relu par avocat + attestation assureur RCP co-construite
4. Lead magnet : « Audit-Vigie express » 30 min gratuit (pattern Dautrey)
