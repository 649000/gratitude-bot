## Context

The Gratitude Jar project currently has a Quarkus REST API deployed via AWS CDK with API Gateway, Firebase JWT auth, and a single Lambda. There is no client. The product vision is a Telegram bot that lets users write gratitude entries, receive periodic digests, rediscover past entries, and export data. The existing architecture is over-engineered for this direction — API Gateway, JWT auth, and the Quarkus runtime add complexity without value when the only client is a Telegram bot.

## Goals / Non-Goals

**Goals:**
- Replace the Quarkus REST API with a Python-based Telegram bot
- Two Lambda functions: one for Telegram webhook handling (fast responses), one for scheduled digest/reminder/rediscovery dispatch
- Timezone-aware scheduling for all push messages
- Digest cadences: weekly (Sunday), monthly (last day), yearly (Dec 31)
- Random rediscovery (~4-6x/user/week) plus on-demand `/surprise`
- Evening reminders to write (7-9pm user local, only if no entry that day)
- Highlight selection using star + length + entity signals
- Inline buttons for star, delete, pagination, preference toggles
- User preferences stored in Supabase PostgreSQL
- Terraform for all infrastructure (replaces CDK)
- S3 backend with DynamoDB state locking for Terraform
- API Gateway HTTP API for Telegram webhook only (single POST /webhook route, no authorizer, no custom domain, no REST endpoints)

**Non-Goals:**
- Multi-user / shared jar functionality (future)
- Photo or media attachments in entries (future)
- AI-powered summarization
- Mobile/web client beyond the Telegram bot
- Real-time sync or offline support

## Decisions

### Architecture: Two Python Lambdas (Webhook + Scheduler)
**Why:** Telegram webhooks require fast responses (<3s). Digest generation queries many users, builds messages, and calls Telegram API — potentially taking minutes. Separate Lambdas avoid timeout issues and allow independent scaling. The webhook Lambda stays lean and cold-starts quickly; the scheduler Lambda can be heavier.

### Python over Java/Quarkus
**Why:** `python-telegram-bot` is the most mature and widely-used Telegram bot framework. Python's ecosystem for text processing, date/time handling, and HTTP clients is simpler than Java for this use case. The existing Quarkus code has no client and no tests — rewriting in Python is lower cost than maintaining both runtimes.

### Supabase PostgreSQL retained
**Why:** The data model (users, entries, timestamps) is simple. PostgreSQL is already provisioned and working. No reason to migrate. Existing tables will be adapted or recreated for the new schema (adding `preferences`, `prompts`, `starred` fields).

### Entity clustering for highlight variety
**Why:** Pure random selection often picks multiple entries mentioning the same person/thing. Entity clustering (tokenize → group by shared keywords → pick one per group) produces a more curated feel without AI. Implementation is ~50 lines of Python.

### Location-based timezone + manual override
**Why:** Telegram provides user location. A single API call (`https://api.telegram.org/bot<token>/getUserProfilePhotos` for location, or the user sending their location via inline keyboard) gives coordinates. `timezonefinder` or `geopy` + `pytz` derives the timezone. Manual `/timezone` command covers edge cases (travel, inaccurate location).

### Terraform over CDK
**Why:** Terraform is more widely adopted, has simpler HCL syntax vs. Java CDK, and separates infra code from application code. S3 backend with DynamoDB locking provides safe state management. The existing CDK stacks will be destroyed before Terraform apply.

### S3 backend with DynamoDB state locking
**Why:** Remote state in S3 enables collaboration and disaster recovery. DynamoDB prevents concurrent state modifications that could corrupt infrastructure.

### API Gateway HTTP API for webhook only (no REST API)
**Why:** Telegram needs a public URL to POST updates to. A single `POST /webhook` route on API Gateway HTTP API is the simplest way to expose the Lambda. No authorizer — Telegram validates requests via the secret token set during webhook registration. No custom domain needed. No REST endpoints — the webhook is the only route. Lambda Function URL was considered but API Gateway provides built-in throttling, request logging, and a consistent URL scheme if more routes are ever needed.

### EventBridge for scheduling
**Why:** EventBridge cron rules trigger the Scheduler Lambda. Each trigger carries a payload (`{"type": "weekly" | "monthly" | "yearly" | "reminder" | "rediscovery"}`) so the Lambda knows which action to take.

### Inline buttons over reply-based interaction
**Why:** Reply-to-star requires an extra step. Inline buttons on each message (⭐ Star, 🗑 Delete) are instant and are standard Telegram UX. Pagination (◀️ ▶️) for `/entries` follows the same pattern.

## Risks / Trade-offs

- **Risk:** Two Lambdas sharing a Telegram Bot Token — if one misbehaves, both are affected. **Mitigation:** Single token stored in Secrets Manager, both Lambdas read it at cold start.
- **Risk:** Entity clustering may produce false groupings (e.g., "Sunrise" as an event vs. "Sunrise Cafe"). **Mitigation:** Keep the algorithm simple and transparent — if accuracy matters later, add a user feedback mechanism.
- **Risk:** Cold starts on the webhook Lambda cause noticeable delay in Telegram responses. **Mitigation:** Keep dependencies minimal (no heavy frameworks), use provisioned concurrency if needed.
- **Risk:** Users in extreme timezones (UTC-12, UTC+14) may have edge cases in scheduling. **Mitigation:** Round to nearest half-hour offset; pytz handles DST transitions.
- **Trade-off:** Single Lambda for all scheduled tasks (reminders, digests, rediscovery) vs. one per type. Single is simpler to deploy and maintain; if one task blocks (e.g., yearly digest querying millions of entries), it delays others. Start with one, split only if performance dictates.
- **Trade-off:** Raw Telegram API calls (`httpx`) vs. `python-telegram-bot` framework. Framework provides webhook setup, update parsing, and callback handling out of the box. Slight cold-start penalty (~100ms) is acceptable.
- **Risk:** CDK stacks currently deployed must be destroyed before Terraform applies — any downtime between destroy and apply. **Mitigation:** Destroy old CDK stacks, then immediately apply Terraform. The bot is not yet in production use, so downtime is acceptable.
