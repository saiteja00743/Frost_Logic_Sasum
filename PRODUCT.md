# ClauseGuard: first customer workflow

Audience: small businesses managing vendor and SaaS agreements. The outcome is a recorded decision before a contractual deadline.

## Implemented

1. Upload a searchable PDF or use a prepared sample.
2. Review source-linked findings and extracted date suggestions.
3. Confirm an action deadline and internal owner. Optionally calculate a notice deadline by subtracting a calendar-day notice period from a renewal date.
4. Track all contracts and actions in the workspace. Search by contract, action, or owner; filter by status.
5. Receive in-app reminders at 30, 7 and 1 day before the deadline, on the due day, and once overdue. The worker checks every minute and the inbox catches up on load. It delivers the current milestone after downtime instead of a burst of stale reminders.
6. Export an all-day calendar event with reminder alarms. Calendar applications control alarm delivery. This is a download, not a live calendar sync; re-import changes and remove obsolete events in your calendar.
7. Record completion, cancellation or reopening with a required note. Changes and confirmation details are saved in an activity ledger.

Internal owner names are labels within a single user's workspace. This version has no team invitations, shared organization workspace, email delivery, e-signature, recurring renewal generation or automatic cancellation notices. A completed action does not cancel a vendor contract.

## Trust and coverage

- JWT signatures, audience, issuer and expiry are checked. Supabase supports HS256 with the configured secret and asymmetric signing via its JWKS endpoint.
- Record ownership is checked on document, analysis, report and workflow access. Legacy records with no established owner remain inaccessible to new signed sessions; do not automatically assign them to a new user.
- Demo sessions are signed and enabled explicitly. Demo is disabled by default on the standard server. Demo data is isolated by session and is not migrated when someone signs in.
- Only exact normalized source matches receive the source-match label. Approximate matches require review. Matching text does not validate interpretation, completeness or a date calculation.
- Every accepted page is submitted for analysis. Limits are 25 MB, 100 pages and 250,000 extracted characters. Pages without text are rejected with an OCR instruction; OCR is not implemented. Sparse or partially scanned pages can still require manual inspection.
- AI failure falls back to a limited local rules engine, not another external provider. The interface identifies the engine. Rules can miss clauses; low review scores are not assurances of safety.
- Confirmed actions require a date, owner, time zone and explicit human confirmation. Editing a date in the form clears the confirmation checkbox. Concurrent stale updates are rejected.

## Storage and hosting

The pilot targets one application instance with a persistent disk. Document metadata and analyses use SQLite by default, or the existing Supabase adapter when configured. Actions, audit events, and reminders use SQLite in `DATA_DIR` in both modes. Uploaded PDFs also require that disk. Do not deploy this version on ephemeral storage or scale it across independent disks. A configured Supabase failure now fails visibly instead of silently splitting records between stores.

Use `backend/supabase_schema.sql` for a new remote document store. Existing deployments must compare their schema and policies before applying it. Keep the service key backend-only. Back up both the database and uploads, verify restoration, and apply authentication configuration before a customer pilot.

The repository's existing Render manifests are historical deployment examples. Confirm a disk-capable hosting plan, environment variables, allowed frontend origin and HTTPS before deploying. No production deployment is performed by this change.

## Validation

`backend/test_product.py` runs offline against a temporary database. It covers forged tokens, tenant isolation, confirmation validation, notice date arithmetic, source ownership, duplicate action prevention, edit conflicts, status history, timezone-aware reminders, deduplication, calendar escaping, negated quotations, full-page request coverage and PDF upload through report export.

Frontend verification: production build, scoped lint, and browser walkthrough of a sample analysis, confirmed action, delivered reminder, completion and reload persistence. Live Supabase OAuth and external AI providers need staging validation with the deployment's credentials.

## Pilot success criteria

Recruit 3–5 small operations teams and measure corrected extraction fields, time to confirm a deadline, actions completed before deadlines, missed reminders, and weekly returning users. Use these findings to prioritize email delivery, shared workspaces and recurring renewal schedules before broadening contract categories.
