## 1. Project Setup

- [ ] 1.1 Create Python project structure for webhook and scheduler Lambdas
- [ ] 1.2 Set up Python virtual environment and dependencies (`python-telegram-bot`, `psycopg2-binary`, `pytz`, `timezonefinder`)
- [ ] 1.3 Create shared database connection module for Supabase PostgreSQL
- [ ] 1.4 Set up CDK stacks for new Python Lambdas (WebhookStack, SchedulerStack)
- [ ] 1.5 Add Telegram Bot Token to AWS Secrets Manager
- [ ] 1.6 Remove old Quarkus `api/` module and CDK stacks (LambdaStack, APIGatewayStack)

## 2. Database Schema

- [ ] 2.1 Create `user_preferences` table (chat_id, timezone, digest_*_enabled, rediscovery_enabled, reminder_enabled)
- [ ] 2.2 Add `starred` boolean column to existing `gratitude` table
- [ ] 2.3 Create `prompts` table (id, text, category) and seed with initial prompts
- [ ] 2.4 Write migration script to carry over existing entries to new schema

## 3. Telegram Webhook Lambda

- [ ] 3.1 Implement webhook registration (set webhook URL on Lambda startup)
- [ ] 3.2 Implement update dispatcher (routes Telegram updates to appropriate handlers)
- [ ] 3.3 Implement inline button callback handler (⭐ Star, 🗑 Delete, ◀️ ▶️, preference toggles)

## 4. Command Handlers

- [ ] 4.1 Implement `/start` — onboarding flow with timezone selection and preference toggles
- [ ] 4.2 Implement `/grateful` — random prompt + save entry flow
- [ ] 4.3 Implement `/surprise` — random past entry with inline buttons
- [ ] 4.4 Implement `/entries` — interactive drill-down (year/month/day) and direct date queries with pagination
- [ ] 4.5 Implement `/settings` — view and toggle all preferences
- [ ] 4.6 Implement `/timezone` — manual timezone override
- [ ] 4.7 Implement `/export` — generate and send entry file
- [ ] 4.8 Implement `/help` — list all commands

## 5. Highlight Selection Algorithm

- [ ] 5.1 Implement weighted scoring function (starred + length + entity diversity)
- [ ] 5.2 Implement entity clustering and de-duplication logic
- [ ] 5.3 Implement digest message builder with inline button markup

## 6. Scheduler Lambda

- [ ] 6.1 Implement EventBridge event router (parse `type` from payload)
- [ ] 6.2 Implement timezone-aware user eligibility query
- [ ] 6.3 Implement daily reminder task (evening, only if no entry today)
- [ ] 6.4 Implement weekly digest task (Sunday evening)
- [ ] 6.5 Implement monthly digest task (last day of month evening)
- [ ] 6.6 Implement yearly digest task (Dec 31 evening)
- [ ] 6.7 Implement rediscovery dispatch (random intervals, 4-6x/week, daytime window)
- [ ] 6.8 Implement error handling and logging (skip blocked users, continue)

## 7. CDK Infrastructure

- [ ] 7.1 Create Webhook Lambda stack (Python runtime, env vars for DB + bot token)
- [ ] 7.2 Create Scheduler Lambda stack (Python runtime, env vars for DB + bot token)
- [ ] 7.3 Create EventBridge rules for each scheduled task (reminder, weekly, monthly, yearly, rediscovery)
- [ ] 7.4 Create Telegram webhook URL integration (API Gateway HTTP or Lambda function URL)
- [ ] 7.5 Add environment variable configuration (Supabase URL/credentials, Telegram token)

## 8. Testing

- [ ] 8.1 Write unit tests for highlight selection algorithm
- [ ] 8.2 Write unit tests for timezone-aware scheduling logic
- [ ] 8.3 Write integration tests for database operations
- [ ] 8.4 Write integration tests for Telegram message formatting
- [ ] 8.5 Deploy to dev environment and test full flow end-to-end

## 9. Cleanup

- [ ] 9.1 Remove Quarkus `api/` module from Maven build
- [ ] 9.2 Remove CDK Java stacks (LambdaStack, APIGatewayStack, EventBridgeStack)
- [ ] 9.3 Update project README with bot usage instructions
- [ ] 9.4 Clean up unused environment variables and secrets
