# Étude de cas — Reverse engineering d'Easy!Appointments 1.6.0 (instance réelle)

> Méthode : analyse de dépôt sur l'instance qui tourne (PHP/CodeIgniter, GPL-3.0 — pas de
> décompilation), lecture ciblée + grep + SQL + probes HTTP. Toute affirmation ci-dessous
> est étiquetée [V] = vérifiée par exécution, ou [L] = lue dans le code (fichier:ligne).
> Cible : sandbox jetable 18081 (`ea-test-app` / `ea-test-db`), données fictives.
> Session : 20261012_175939_35be5a · date : 2026-10-12.

## 1. Contexte

Objectif : comprendre de l'intérieur la plateforme telle qu'elle tourne (pas depuis la doc)
et en extraire des patterns réutilisables pour Vagus OS. Livrable = cartographie + confrontation
à nos skills en 3 buckets + patterns volables.

Périmètre tranché : le dépôt amont est open source, donc REA (décompilation binaire) est
l'outil inadapté. L'analyse est faite en lecture de code + probes sur l'instance réelle.
Si la cible voulue devient l'image packagée ou un SaaS concurrent (Calendly, Cal.com),
c'est un autre chemin (un benchmark Cal.diy existe déjà dans `log.md`, session d472259ab897).

## 2. Faits mesurés (preuves d'exécution)

| Fait | Preuve |
|---|---|
| API v1 : 401 sans jeton, 200 avec Basic admin | déjà prouvé par la session précédente, non refait |
| `POST /api/v1/appointments` accepte des RDV **chevauchants sans aucune vérification** | [V] 3 RDV identiques créés (09:00-09:30, même prestataire 2) → ids 1, 2, 3 ; HTTP 201 à chaque fois |
| Le chemin public refuse, lui, le doublon | [V] 8 requêtes concurrentes sur 2026-10-16 10:00 → 1 seul `appointment_id`, 7 réponses « not available » |
| Le rejet métier du chemin public est renvoyé en **HTTP 500** | [V] `{"success":false,"message":"The requested appointment is unfortunately not available…"}` en 500 |
| Webhook sortant : POST JSON `{action,payload}`, User-Agent `GuzzleHttp/7` | [V] capturé par un listener PHP dans le conteneur |
| L'appel webhook est **synchrone et bloque la requête** | [V] récepteur qui dort 3 s → le `POST /appointments` répond en 3,26 s |
| Récepteur HS → la réservation passe quand même | [V] 0,25 s, HTTP 201, erreur journalisée, aucun rejeu |
| Contrôleur API `working_plan_exceptions` **non routé** (dead code) | [V] `GET /api/v1/working_plan_exceptions` → 404 ; `service_categories` → 200 |
| L'API webhooks ne peut pas définir `secret_header` (absent du mapping) et ignore silencieusement un champ mal nommé | [V] `secret_token` dans le POST → `secret_token = NULL` en base, HTTP 201 sans erreur ; `secretToken` → persisté |
| Rôle « any-provider » : le prestataire choisi est celui qui a le **plus de créneaux libres** | [L] `Booking.php:661-690` |

## 3. Cartographie

### 3.1 Modèle de données — 14 tables (MySQL 8, FK en cascade)

Bloc identité (le piège du produit) :
- `ea_users` — profil : nom, email, téléphones, adresse, `timezone`, `language`,
  `custom_field_1..5`, `is_private`, `ldap_dn`, `id_roles`.
- `ea_user_settings` — **c'est là que sont `username` et `password`** (bcrypt 60 car.,
  champ `salt` redondant), plus tout l'état connecteur : `working_plan` (JSON),
  `working_plan_exceptions`, `google_sync/token/calendar`, `caldav_sync/url/username/password`,
  `sync_past_days` (30), `sync_future_days` (90), `calendar_view`. Une ligne par utilisateur
  (PK = `id_users`). [L] schéma + [V] `SHOW CREATE TABLE`
- `ea_roles` — RBAC : 4 lignes (admin, provider, customer, secretary) avec une matrice
  d'entiers de droits par entité (`appointments`, `customers`, `services`, `users`,
  `system_settings`, `user_settings`, `webhooks`, `blocked_periods`). [V] valeurs observées :
  admin 15 partout, provider 15/15/0/0/0/15/0/0, customer 0 partout, secretary 15/15/0/0/0/15/0/0.
- `ea_secretaries_providers` — table de liaison N-N secrétaire ↔ prestataire.

Bloc catalogue :
- `ea_services` — `duration` (min), `slot_interval` (défaut 15), `price`, `currency`, `color`,
  `location`, `attendants_number` (1 = mono, >1 = séance de groupe), `is_private`,
  `id_service_categories`. `slot_interval` **découplé** de `duration` (migration 061) :
  pas de la grille ≠ longueur du RDV.
- `ea_service_categories`, `ea_services_providers` (N-N prestataire ↔ service).

Bloc temps — le cœur :
- `ea_appointments` — **timeline unique** : `start_datetime`/`end_datetime`, `book_datetime`,
  `hash` (12 car., lien public de gestion), `color`, `status`, `location`, `meeting_link`
  (Jitsi, migration 062), `id_google_calendar` / `id_caldav_calendar` (références externes),
  et surtout `is_unavailability` : le même enregistrement sert de RDV **ou** de bloc
  d'indisponibilité importé d'un calendrier externe.
- `ea_unavailabilities` — n'existe pas comme table : les indisponibilités sont des lignes
  `ea_appointments` avec `is_unavailability = 1` (cf. `delete_caldav_recurring_events`).
- `ea_blocked_periods` — blocage global de l'instance (jours fériés, fermeture), sans prestataire.
- `ea_working_plan_exceptions` — exception datée par prestataire (`start_date`, `end_date`,
  `start_time`, `end_time`, `breaks` JSON) ; surcharge le plan hebdomadaire pour une date.
- `ea_consents` — preuve de consentement : `type` (terms-and-conditions / privacy-policy),
  `ip`, horodatage, nom/email dénormalisés, FK `id_users` ON DELETE SET NULL.
- `ea_webhooks` — `url`, `actions` (CSV), `secret_header` (défaut `X-Ea-Token`),
  `secret_token`, `is_ssl_verified`.
- `ea_settings` — 80 lignes clé/valeur (`name`/`value` longtext) dont `api_token`,
  `book_advance_timeout` (30 min), `future_booking_limit` (90 j), `require_captcha`,
  `altcha_enabled`, `disable_booking`, `data_retention_days`, plan `company_working_plan`.
- `ea_migrations` — une seule colonne `version` (ici 69).

### 3.2 Surface d'API (v1)

- Auth : Basic admin **ou** Bearer `api_token` (comparaison `hash_equals`, [L] `Api.php:65-94`).
  Pas de clé par consommateur, pas de scopes, pas de quota par clé — un seul jeton global.
- 13 contrôleurs v1. 10 ressources CRUD routées (`appointments`, `admins`, `customers`,
  `providers`, `secretaries`, `services`, `service_categories`, `unavailabilities`,
  `blocked_periods`, `webhooks`) + `settings` (GET liste / GET clé / PUT clé) +
  `availabilities` (GET). `working_plan_exceptions` existe mais **n'est pas routé** → 404 [V].
- Conventions uniformes portées par une lib unique (`libraries/Api.php`) : pagination
  `page`/`length` (défaut **20**), tri `sort=-field,+field` avec **whitelist** via
  `model->db_field()` (un champ inconnu est ignoré, pas d'erreur — garde anti-injection),
  projection `fields=`, relations `with=service,provider,customer`, recherche `q=`.
- Chaque modèle porte son mapping `api_resource` + `api_encode/api_decode` : le contrat
  d'API est **déclaré par ressource**, pas écrit à la main dans les contrôleurs.
- Deux chemins d'écriture pour un même objet :
  - **API admin** `POST /api/v1/appointments` : validation de forme seulement (champs requis,
    format datetime, durée ≥ 5 min, existence des FK) → **aucun contrôle de disponibilité ni
    de chevauchement** [V].
  - **Chemin public** `POST /index.php/booking/register` : CSRF double-submit (cookie ==
    `csrf_token`, non rotatif), captcha/ALTCHA optionnels, **re-vérification de la
    disponibilité juste avant l'insert**, refus si le client a déjà un RDV sur le créneau,
    écriture des consentements, notification + sync + webhook.

### 3.3 Logique de disponibilité (le cœur du produit)

`libraries/Availability.php` (647 l.) — pipeline en 4 temps :

1. `get_available_periods(date, provider)` : part du `working_plan` JSON du prestataire
   (`monday…sunday` → `{start, end, breaks[]}`), le **remplace** par l'exception datée si
   `working_plan_exceptions[date]` existe, puis soustrait les intervalles occupés en
   fusionnant trois sources de « temps pris » : `ea_appointments` + `ea_unavailabilities`
   (même table filtrée) + `ea_blocked_periods` du jour. `exclude_appointment_id` permet
   d'exclure le RDV en cours d'édition (sinon on se bloque soi-même).
2. `generate_available_hours()` : échantillonne chaque période libre du **pas** `slot_interval`
   (défaut 15 min) tant qu'il reste ≥ `duration`.
3. `consider_book_advance_timeout()` : supprime les heures ≤ maintenant + `book_advance_timeout`
   (30 min), calculé **dans le fuseau du prestataire**.
4. `consider_future_booking_limit()` : retourne `[]` si la date dépasse maintenant +
   `future_booking_limit` (90 j).

Cas particulier `attendants_number > 1` : autre algorithme
(`consider_multiple_attendants`) qui compte les places restantes au lieu de retirer le créneau.

Le « any-provider » résout la ressource au moment du commit : parmi les prestataires du
service, il prend celui qui offre le plus de créneaux ce jour-là (et qui contient l'heure
demandée). [L] `Booking.php:661-690`.

Anti-collision : `check_datetime_availability()` **recalcule** les créneaux et exige que
l'heure demandée y figure encore, juste avant l'insert [L] `Booking.php:603-646`.
`has_provider_conflict()` (test de chevauchement SQL propre) existe mais n'est appelé **que**
par `Calendar.php:332` (création manuelle au back-office) — pas par l'API [V par grep].

### 3.4 Extensibilité

- **CodeIgniter 3 patché** : toutes les classes core sont des `EA_*` qui étendent les `CI_*`
  (EA_Controller, EA_Model, EA_Hooks, EA_Migration, EA_Input, EA_Security…) → point
  d'extension par surcharge de classe, sans toucher au vendor.
- **Hooks CI** : 2 seulement (`application/config/hooks.php`) — `security_headers`
  (post_controller_constructor) et `storage_cleanup` (post_system, exécuté sur ~1 % des
  requêtes, purge sessions/logs/cache > 90 j) [L+V code].
- **Migrations** : 70 fichiers numérotés, append-only, une seule ligne `version` en base ;
  CLI `php index.php console migrate|install|seed|backup|sync|cleanup`.
  Pas de down() réel, pas de rollback — évolution strictement avant.
- **Thèmes** : sélection via `?theme=` whitelistée sur `assets/css/themes/*.min.css`
  (sanitisation anti-traversée) → 5-6 variantes + `default`.
- **i18n** : 21+ dossiers de langue, fichiers PHP plats par clé (`application/language/<lang>/`).
- **Champs personnalisés** : `custom_field_1..5` sur `ea_users` avec libellés stockés dans
  `ea_settings` → extension de schéma sans migration.
- **Webhooks** : 18 actions (`appointment_save/delete`, `customer_*`, `service_*`,
  `provider_*`, `secretary_*`, `admin_*`, `blocked_period_*`, `unavailability_*`),
  payload `{action, payload}` en JSON, en-tête secret configurable.
- **Pas de système de plugins/modules.** Toute extension profonde = fork (GPL-3.0 →
  obligation de fournir la source) ; white-label/revente = licence étendue payante.

### 3.5 Angles morts structurels

1. **Asymétrie des gardes** : le chemin public protège la ressource rare, l'API
   d'administration ne la protège pas. Une intégration (n8n, script) qui écrit via l'API
   peut créer des collisions que l'UI publique n'aurait jamais permises.
2. **Check-then-act non atomique** : la re-vérification au commit réduit la fenêtre mais
   rien en base ne l'interdit (pas de contrainte d'unicité, pas de verrou). Mesuré : tient
   sur 8 requêtes concurrentes locales — ce n'est pas une preuve d'atomicité.
3. **Webhook synchrone, sans rejeu, sans signature** : secret en en-tête statique (pas de
   HMAC sur le corps), pas de file d'attente, pas de retry, latence du récepteur infligée
   au client, perte silencieuse si le récepteur est HS.
4. **Qualité de contrat d'API** : un rejet métier sort en 500 ; un champ mal orthographié est
   ignoré sans erreur (faux sentiment de succès) ; `secret_header` non exposé par l'API ;
   un contrôleur livré mais non routé (404).
5. **Pas un moteur de planification** : pas de récurrence, pas de salle/ressource au-delà de
   (prestataire, service), pas de round-robin, pas de paiement, pas de SMS, sync
   Outlook/M365 absente.

## 4. Confrontation à nos skills (3 buckets)

### 4.1 Doublons — le concept est déjà chez nous, ne rien créer

| Ce qu'EA fait | Notre couverture |
|---|---|
| Emails transactionnels + ICS joint + templates | `emailing-campagne`, `envoi-mail-verifie` (nous avons la preuve de délivrabilité, EA fait le transport) |
| Tâches CLI planifiées (`console sync/cleanup/backup`) | `hermes-cron-ops`, `cost-zero-cron-operations`, `shell-regression-harnesses` |
| Configuration clé/valeur globale + helper typé `setting()` | `hermes-config-management` |
| Réconciliation avec une source externe (id de référence en base : `id_google_calendar`, `id_caldav_calendar` ; purge des orphelins) | `hermes-shared-state`, `bidirectional-skill-sync`, `merge-guard-dual-sync` |
| Surveillance d'un état externe par polling planifié (`sync_past_days`/`sync_future_days`) | `veille-etat-externe` |
| Journal d'exécution / preuves d'action | `run-receipts` |

### 4.2 Complémentaires — pattern EA à verser dans une skill existante

| Pattern EA (preuve) | Skill à enrichir |
|---|---|
| Fenêtres autorisées/interdites paramétrables : plan hebdo + **exceptions datées** + blocages globaux + avance minimale + horizon max | `cost-zero-cron-operations` (nous arbitrons peak/off-peak DeepSeek à la main, sans table d'exceptions ni horizon typé) |
| Timeline unique : RDV, indisponibilité, blocage et événement externe = une table + flag `is_unavailability` | `agenda-copilot` (modèle plus simple que notre empilement de sources) |
| Anti-collision par re-vérification au commit + exclusion de l'entité en cours d'édition (`exclude_appointment_id`) | `merge-guard-dual-sync`, `hermes-shared-state` (nos écritures partagées ne revérifient pas l'état au dernier moment) |
| Preuve de consentement (type, IP, horodatage, identité dénormalisée) + rétention (`data_retention_days`) | `cgv-conformite-consommation-france` (volet technique manquant : la preuve, pas le texte) |
| Jeton d'édition court non devinable (cache 10 min) pour modifier sans compte | `espace-validation-publication` (lien de validation signé à durée de vie) |
| Liste blanche fail-closed (tri API : champ non whitelisté ignoré ; projection par `array_intersect_key`) | `deny-rules-gateway`, `audit-securite-repository` (question d'audit à ajouter : *chaque chemin d'écriture a-t-il le même garde ?*) |
| Choix de ressource par capacité objective (« le plus de créneaux libres ») | `delegation-fanout-research`, `vagus-os-orchestration` (sélection d'agent/modèle : critère mesurable plutôt qu'affinité) |
| Extension de schéma sans migration (champs custom + libellés en settings) | `document-rag-ingestion`, `vkg-engine` |
| Maintenance amortie dans le trafic (~1 % des requêtes) au lieu d'un cron | `cost-zero-cron-operations` (variante « entretien opportuniste » quand il n'y a pas de trafic garanti) |

### 4.3 Gaps — rien chez nous, matière à concevoir

1. **Moteur de créneaux** : aucune doctrine sur grille horaire (pas ≠ durée), chevauchement,
   fuseau par ressource, avance minimale, horizon max, exceptions datées. → concept créé
   (`concepts/moteur-disponibilite-creneaux.md`).
2. **Anti-double-réservation de nos actions à effet réel** : nous savons ne pas *inventer* un
   résultat (`run-receipts`), nous n'avons pas de doctrine pour ne pas *écraser/dupliquer*
   (check-then-act, idempotence, clé de dédup).
3. **Contrat d'API minimal réutilisable** pour nos livrables (auth unique, pagination,
   tri whitelisté, projection, relations, erreurs métier ≠ 500).
4. **Receveur de webhook** (vérifier le secret, idempotence par id, rejeu) — côté n8n sans
   doute, mais non capitalisé.
5. **Évolution de schéma** (migrations append-only numérotées + version unique + CLI
   migrate/backup) — utile dès qu'un livrable client a des données.
6. **Rénovation d'une app livrée** : la démarche de cette session (lire le handoff → vérifier
   les faits « déjà prouvés » → attaquer les asymétries par probes → nettoyer le sandbox)
   n'est écrite nulle part.

## 5. Patterns volables (isolés, avec preuve)

1. **Re-vérification au commit** — recalculer la ressource rare juste avant l'écriture et
   exiger que le choix demandé soit encore dans le résultat. `Booking.php:603-646`
   [V] 8 requêtes concurrentes → 1 gagnant.
2. **Exclusion de soi-même** — tout calcul de contrainte doit pouvoir exclure l'entité en
   cours d'édition (`exclude_appointment_id`), sinon modification = conflit avec soi-même.
   `Availability.php:334-361`.
3. **Timeline unique avec drapeau** — un seul enregistrement pour « occupé » : interne,
   indisponibilité, blocage externe. `ea_appointments.is_unavailability`,
   `Appointments_model::delete_caldav_recurring_events:339`.
4. **Plan par défaut + table d'exceptions datées** — surcharge ponctuelle sans dupliquer le
   plan ; remplace le plan du jour, ne s'y ajoute pas. `Availability.php:377-380` +
   migration 065/066.
5. **Pas de créneau ≠ durée** — deux paramètres distincts (`slot_interval` / `duration`),
   migration 061 : on peut proposer toutes les 15 min un RDV de 30 min.
6. **Filtres temporels dans le fuseau de la ressource** — avance minimale et horizon max se
   calculent avec le fuseau du prestataire, pas celui du serveur. `Availability.php:588-646`.
7. **Résolution de ressource par capacité** — quand le demandeur ne choisit pas, résoudre sur
   un critère objectif (« le plus de créneaux libres ») et vérifier la contrainte demandée.
   `Booking.php:661-690`.
8. **Contrat d'API déclaré par ressource** — mapping `api_resource` + `api_encode/api_decode`
   sur le modèle, conventions (pagination/tri/projection/relations) portées par une lib
   unique, tri **whitelisté** et échec silencieux sur champ inconnu. `libraries/Api.php:176-267`,
   `EA_Model::db_field()`.
9. **Webhook minimal** — `POST {action, payload}` JSON, secret en en-tête configurable,
   échec journalisé sans casser la transaction métier. `Webhooks_client.php:74-104` [V].
   Version durcie à nous : HMAC sur le corps + file d'attente + rejeu + idempotence.
10. **Entretien amorti dans le trafic** — hook probabiliste 1 % au lieu d'un cron.
    `hooks/storage_cleanup.php` [V].
11. **Preuve de consentement** — table dédiée (type, IP, horodatage, identité dénormalisée)
    écrite au moment de l'acceptation, indépendante du compte. `ea_consents`,
    `Booking.php:511-529`.
12. **Jeton d'édition court** — accès en modification sans compte via un jeton aléatoire en
    cache à durée de vie courte (10 min). `Booking.php:284-287`.

## 6. Verdict

**Outil : bon socle de prise de RDV mono-instance, moteur de disponibilité simple et
lisible, correct dans son périmètre. En tant que *plateforme* à intégrer, il présente deux
failles de conception, pas des bugs : (a) l'API d'écriture ne protège pas la ressource rare
alors que le chemin public la protège ; (b) les webhooks sont synchrones, sans rejeu ni
signature.** Pour un usage « notre site de réservation », c'est exploitable tel quel ;
pour un usage « brique de notre architecture », il faut un médiateur qui tienne les
invariants (dédup, file d'attente) — sinon on importe la faille.

**Pour Vagus OS, la valeur n'est pas le produit mais trois idées** : la timeline unique à
drapeau, le plan + exceptions datées, et la re-vérification au commit. La comparaison
Cal.diy (`log.md`, 12/10) reste valide : EA est ~4× plus léger en RAM, installé en CLI,
sans build — mais moins riche (pas de teams/routing/workflows/paiement).

**Recommandation** : garder la sandbox tant que la décision de promotion n'est pas prise
(elle sert de banc d'essai), et ne pas déployer une intégration qui écrit des RDV via l'API
sans garde applicatif.

## 7. Reste ouvert

- Décision JP : démonter la sandbox ou la promouvoir derrière Traefik + HTTPS (sauvegardes).
- Candidat skill (à valider) : `moteur-creneaux-anti-collision` (gaps 4.3-1 et 4.3-2).
- Non testé : comportement en cas de collision sur `attendants_number > 1` (séance de groupe),
  sync CalDAV/Google réelle (aucun serveur CalDAV branché sur la sandbox).
