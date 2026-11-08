# Research 01: Strava API for personal use

Ticket: `tickets/01-research-strava-api.md`. Researched 2026-11-08. Sources are official Strava pages only.
Method note: pages were read via a summarizing fetch tool, not raw HTML. Items marked **[UNVERIFIED]** need a manual check.

## Sources

- Getting started: https://developers.strava.com/docs/getting-started/
- Authentication: https://developers.strava.com/docs/authentication/
- Rate limits: https://developers.strava.com/docs/rate-limits/
- Webhooks: https://developers.strava.com/docs/webhooks/
- API reference: https://developers.strava.com/docs/reference/
- API Agreement: https://www.strava.com/legal/api

## 1. App registration (getting-started)

- Create the app at https://www.strava.com/settings/api. A Strava subscription is required to create an app (per getting-started page) **[UNVERIFIED: confirm in your account; the plan requirement may have changed]**.
- Registration yields Client ID, Client Secret (keep private), and an initial access/refresh token on the app page.
- "Authorization Callback Domain" field: `localhost` is allowed for development.
- New apps start in **Single Player Mode**: only the owner's own account can authorize. Fits this project (single user).
- Upgrading from the API Settings Dashboard raises capacity to 10 athletes; more than 10 needs app review (rate-limits page). Out of scope here.

## 2. OAuth flow and token refresh (authentication)

- Flow: redirect to `GET https://www.strava.com/oauth/authorize` -> user approves -> redirect back with `code` and `scope` -> `POST https://www.strava.com/oauth/token` with `client_id`, `client_secret`, `code`, `grant_type=authorization_code`.
- The code is short-lived and single-use. Check the returned `scope`: the user can uncheck scopes.
- Scopes relevant here:
  - `activity:read`: Everyone/Followers activities, no privacy-zone data. Required for activity webhooks.
  - `activity:read_all`: adds privacy-zone data and "Only You" activities. Needed to see all of the owner's own activities.
- Access tokens expire after 6 hours (`expires_in: 21600`).
- Refresh: `POST /oauth/token` with `grant_type=refresh_token`.
  - If more than 1 hour remains, the same access token is returned; otherwise a new one.
  - A refresh may return a new refresh token; the old one is invalidated immediately. Always persist the latest refresh token.
- Deauthorize: `/oauth/revoke` is recommended from 2026-06-01 and the only supported endpoint from 2027-06-01; `/oauth/deauthorize` is the older one.
- Consequence for spec: the local app must store the client secret and the latest refresh token securely (outside git).

## 3. Rate limits (rate-limits)

- Defaults per app: overall 200 req / 15 min and 2,000 / day; non-upload 100 req / 15 min and 1,000 / day.
- A separate default read limit is not stated on the page **[UNVERIFIED]**; the page's upgraded-app section lists read 200 / 15 min and 2,000 / day.
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Usage`, `X-ReadRateLimit-Limit`, `X-ReadRateLimit-Usage` (values "15-min,daily").
- Exceeding returns HTTP 429. Windows reset at :00/:15/:30/:45; daily resets at midnight UTC.
- Strava advises webhooks over polling and throttling backfills by headers.
- Consequence: a full backfill of N activities needs ~N/per_page list calls (cheap). Fetching per-activity detail/laps costs 1 call each; at about 100 per 15 min, a large history needs throttled, resumable sync.

## 4. Activity data (reference)

Endpoint `GET /athlete/activities`:
- Params: `before`, `after` (epoch ints), `page` (default 1), `per_page` (default 30).
- Max `per_page` is not stated in the fetched text **[UNVERIFIED]**; check the Swagger page.
- Activities with "Only Me" visibility are excluded unless the token has `activity:read_all`.
- Pagination is page-number based; use `after` for incremental sync.

SummaryActivity fields (reference schema):
- Identity/time: id, external_id, upload_id, name, start_date, start_date_local, timezone
- Type: sport_type (type is deprecated), workout_type, trainer, commute, manual, private, flagged
- Metrics: distance, moving_time, elapsed_time, total_elevation_gain, elev_high, elev_low, average_speed, max_speed
- Power: kilojoules, average_watts, weighted_average_watts, max_watts, device_watts
- Location: start_latlng, end_latlng, map (id, summary_polyline)
- Social/other: achievement_count, kudos_count, comment_count, athlete_count, photo_count, total_photo_count, device_name, gear_id, tags, hide_from_home
- Heart rate and cadence: `has_heartrate`, `average_heartrate`, `max_heartrate`, `average_cadence`, `suffer_score`, `calories`-like fields appear in the **sample response** but are **not in the SummaryActivity schema** list. **[UNVERIFIED]** whether they are reliably returned in list responses; verify with one real call on the owner's data.
- `location_city/state/country` also appear in the sample response only **[UNVERIFIED]**.

DetailedActivity adds: description, calories, segment_efforts, splits_metric, splits_standard, laps, best_efforts, gear, photos, embed_token (and map.polyline). Sample also shows average_temp **[UNVERIFIED in schema]**. Get it with `GET /activities/{id}` (`include_all_efforts` optional).

Laps: `GET /activities/{id}/laps` returns Lap objects with: id, name, lap_index, split, start_date(+local), elapsed_time, moving_time, distance, start_index, end_index, total_elevation_gain, average_speed, max_speed, average_cadence, pace_zone. Sample also shows average_watts, device_watts. Heart rate per lap is not in the schema list **[UNVERIFIED]**.

Streams (out of scope per map, noted for later): `GET /activities/{id}/streams?keys=...&key_by_type=true`. Types: time, distance, latlng, altitude, velocity_smooth, heartrate, cadence, watts, temp, moving, grade_smooth.

## 5. Polling vs webhooks (webhooks)

- Webhook: one subscription per app, created via `POST https://www.strava.com/api/v3/push_subscriptions` (`client_id`, `client_secret`, `callback_url`, `verify_token`).
- Strava validates the callback with a GET containing `hub.challenge`; the server must echo it as JSON within the time limit.
- Events: activity create/update/delete (update covers title, type, privacy) and athlete deauthorization. Payload: object_type, object_id, aspect_type, updates, owner_id, subscription_id, event_time. The payload carries IDs only; fetch the activity afterwards.
- Callback must return 200 within 2 seconds; up to 3 attempts total.
- The callback must be reachable from Strava's servers, i.e. a public URL (implied, not stated). That conflicts with "local-only" unless a tunnel is used.
- Recommendation for the spec (inference, not from docs): for one user with few new activities per day, polling `GET /athlete/activities?after=<last_synced>` on a schedule or on-demand is well within limits and keeps everything local. Webhooks are optional and add public-endpoint complexity.

## 6. Restrictions on storage and AI use (API Agreement)

- Local storage: the agreement text has no explicit caching or retention-duration rule (retention tied to termination, section 4.4: delete all Strava data on termination).
- Display: Strava Data provided by a user may only be displayed to that user in your app (matches single-user local use).
- Security: must use appropriate measures to protect data obtained from Strava.
- Deletion: on termination, permanently delete API materials and Strava data and certify in writing (4.4).
- **AI/ML:** two fetches found no mention of AI, machine learning, or model training in the page text. **[UNVERIFIED]** Strava has publicly updated API terms around AI in the past; the fetch tool may have missed or truncated clauses. Read https://www.strava.com/legal/api manually (search "AI", "model", "machine learning") before treating local-LLM/RAG use as permitted. Using the owner's own data in a local model, not shared or trained into a distributed model, is the low-risk reading, but that is an inference.
- The agreement is not specific to personal/single-user apps.
- Page metadata date 2026-06-01; no "Last updated" label found.
- Branding: do not use the Strava name beyond Brand Guidelines (8.1). Relevant only if the UI shows Strava marks.

## Open items for follow-up tickets

- Manually confirm the AI clause and the subscription requirement (see UNVERIFIED above).
- Make one real call to `GET /athlete/activities` to confirm which fields (heart rate, suffer_score, location) come back; feeds ticket 05 (schema).
- Ticket 08 (register app): use callback domain `localhost`, scope `activity:read_all`.
