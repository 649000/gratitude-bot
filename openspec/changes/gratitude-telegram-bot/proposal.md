## Why

The Gratitude Jar currently exists as a Quarkus REST API with no consumer. The product vision is a Telegram bot — users write gratitude entries via chat, receive periodic digests (weekly/monthly/yearly), rediscover past entries, and export their data. The REST API has no purpose without a client, and the scheduled EventBridge trigger has no handler. This change transforms the project into the actual product: a Telegram bot that people interact with daily.

## What Changes

- Replace the Quarkus REST API with a Python-based Telegram bot Lambda
- Add a new Python Scheduler Lambda for digest/reminder/rediscovery dispatch (triggered by EventBridge)
- Add Telegram bot webhook handler Lambda processing commands: `/grateful`, `/surprise`, `/entries`, `/settings`, `/export`, `/help`
- Add user onboarding flow with timezone detection (location-based + manual override)
- Add digest scheduling (weekly Sunday, monthly last-day, yearly Dec 31), all timezone-aware
- Add random rediscovery dispatch (~4-6x/week during user daytime)
- Add evening reminder to write (7-9pm user local, only if no entry that day)
- Add highlight selection algorithm (starred boost + length boost + entity clustering)
- Add inline button support (⭐ Star, 🗑 Delete, ◀️/▶️ pagination, preference toggles)
- Add `/export` command for data download
- Remove Quarkus module and CDK stacks (API Gateway, existing Lambda, EventBridge) — replaced by new Python architecture
- Keep Supabase PostgreSQL as the database

## Capabilities

### New Capabilities
- `telegram-bot-commands`: Telegram bot command handlers — `/grateful`, `/surprise`, `/entries`, `/settings`, `/export`, `/help`; inline button callbacks for star, delete, pagination, preference toggles
- `user-onboarding`: User registration flow — `/start` with timezone detection (Telegram location + manual override), opt-in for digest cadences and rediscovery
- `gratitude-writing`: Writing gratitude entries via `/grateful` with random prompts, free-form text entry, and evening reminders (only if no entry that day)
- `digest-delivery`: Scheduled digest dispatch — weekly (Sunday evening), monthly (last day), yearly (Dec 31); highlight selection using star/length/entity signals
- `rediscovery`: Random past entry delivery (~4-6x/week) plus `/surprise` on-demand command; all timezone-aware
- `data-export`: Export all user entries as downloadable file via `/export`
- `highlight-selection`: Algorithm for selecting which entries appear in digests — weighted scoring (starred, length, entity diversity) with de-duplication
- `scheduler-dispatcher`: EventBridge-triggered Lambda that determines which digest type to run, queries eligible users, generates messages, and pushes via Telegram API

### Modified Capabilities

_(None — no existing specs to modify)_

## Impact

- **Remove**: `api/` module (Quarkus), `cdk/` LambdaStack + APIGatewayStack (API Gateway, JWT authorizer, Quarkus Lambda), existing EventBridge handler placeholder
- **Add**: Python-based Telegram webhook Lambda, Python-based Scheduler Lambda, new CDK stacks for both Lambdas + EventBridge rules + Telegram webhook integration
- **Preserve**: Supabase PostgreSQL schema (migrate existing `gratitude` and `app_user` tables or adapt), project-level `openspec/` structure
- **Dependencies**: `python-telegram-bot` (or raw `httpx`), `psycopg2`/`asyncpg` for PostgreSQL, `pytz` for timezone handling
- **Secrets**: Telegram Bot Token added to AWS Secrets Manager or Lambda environment variables
