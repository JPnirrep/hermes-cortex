---
type: concept
timestamp: 2026-10-02
tags: [sandrina, visuels, kdrive, banque-images, ia-genere, droits-image, linktree]
links: [sandrina-ligne-editoriale-20261005, sandrina-livre-hsp]
---

# Sandrina — banque de visuels (état des lieux 02/10/2026)

Inventaire des visuels exploitables pour la communication Sandrina, vérifié par inspection
visuelle réelle (téléchargement kDrive + analyse image), pas par supposition.

## Ce qui est PRÊT et publiable

| Visuel | Emplacement | Note |
|---|---|---|
| `photo ok, sand pour site.png` | `KLEIA-UP/Sandrina/photos de Sand à travailler/seminaire des reveusess 2025` | **La meilleure.** Sandrina sur scène, robe rouge, bras ouverts, confettis dorés, fond violet. Qualité pro. |
| `HPS lâcher prise-les 5 A.png` | `Common documents/Videos et photos/Photos/photos du livre` | Affiche « Mes fameux 5 A » (méthode en 5 étapes). Vertical, propre, prêt. Manque logo/signature. |
| `Ils sont là.jpeg` | idem | 2 exemplaires du livre sur un bureau bois + clavier. **Photo réelle**, bonne qualité. |
| 16 photos séminaire Rêveuses | `KLEIA-UP/Sandrina/photos de Sand à travailler/seminaire des reveusess 2025` | Qualité inégale : `IMG_1505/1519/1520/1521` = smartphone basse lumière, floues/granuleuses → story seulement. |
| 5 Reels montés | `KLEIA-UP/04_MARKETING_ET_COMMUNICATION/Strategie_de_Contenu_Canaux/Instagram_Reels` | HSP video1, je tourne en rond, le bingo, le soutien, A3. |
| 12 vidéos prise de parole | `KLEIA-UP/07_banque d'images et videos/video` | Réemploi long → Short. |
| Montages récents | `Common documents/Videos et photos/Videos/videos montées/` | `260922_videos lancement du livre`, `260928_parution`, `260929-la baignoire`… |

## Ce qui est À ÉCARTER — visuels générés par IA

Vérifiés en gros plan : **faux**, à ne JAMAIS publier en communication réelle.

| Fichier | Défaut constaté |
|---|---|
| `en librairie.png` | 🔴 Le plus dangereux car le plus beau. **Invente des titres de livres qui n'existent pas** (« La magie du matin », « Libérer votre mental », « Rayonner être soi ») sur une prétendue table de librairie. |
| `livre offert-hps-lâcherprise.png` | 🔴 Mains déformées, nom d'autrice tronqué, titre coupé en deux mots. |
| `HPS  lâcher prise sorti du sac.png` | 🔴 Doigts incertains, fermeture du sac incohérente, pas d'auteur affiché. |

**Leçon** : ces trois visuels circulaient comme « photos du livre ». Leur apparence soignée rend le
défaut invisible à l'œil non entraîné. **Toujours inspecter mains / doigts / petit texte / cohérence
du décor avant de proposer un visuel comme publiable.** Un visuel IA présenté comme photo réelle est
un risque d'image pour la marque.

## Contrainte juridique

**Droit à l'image des participantes — ✅ ACCORD DONNÉ (02/10/2026).**
Les participantes du séminaire ont donné leur accord pour la diffusion de leur image.
Les photos du séminaire sont donc **publiables** (mercredi et vendredi débloqués) ; seule contrainte
restante : la **qualité** (`IMG_1505/1519/1520/1521` = smartphone basse lumière → story seulement).

## Méthode de vérification (réutilisable)

1. Lister `rclone lsf` + `rclone lsf --format sp` (tailles = indice de qualité).
2. `rclone copy` les candidats en local (scratch).
3. `vision_analyze` sur chaque candidat — question explicite « photo réelle ou générée par IA ? »
   avec demande d'examen des mains, doigts, textes, répétitions.
4. Pour un texte douteux sur une image : crop PIL puis `vision_analyze` sur le crop (zoom = lecture
   fiable ; le modèle avait annoncé une faute « HYPRSENSIBLES » qui était un artefact de crop).
5. Pour un QR : `pyzbar` (`pip install pyzbar`, nécessite `libzbar.so.0` système, présent ici).
   ⚠️ Essayer **l'inversion** (`ImageOps.invert` / `point(255-v)`) : un QR inversé ne se décode pas
   en positif, et ça se lit comme « QR non scannable » alors qu'il l'est en négatif.
