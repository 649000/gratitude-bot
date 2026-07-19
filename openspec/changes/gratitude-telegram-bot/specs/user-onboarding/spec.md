## ADDED Requirements

### Requirement: Bot onboards new users via /start
The system SHALL guide new users through onboarding: ask for timezone (via Telegram location or manual selection), then prompt for digest and rediscovery preferences.

#### Scenario: User sends /start for the first time
- **WHEN** an unknown user sends `/start`
- **THEN** bot replies with a welcome message and asks for timezone via [📍 Send Location] [🔧 Set Manually]
- **WHEN** user sends their location
- **THEN** bot derives timezone from coordinates and stores it
- **WHEN** user taps 🔧 Set Manually
- **THEN** bot shows a list of UTC offsets to pick from
- **THEN** bot asks which digests they want: [✅ Daily Reminder] [✅ Weekly] [✅ Monthly] [✅ Yearly]
- **THEN** bot asks [✅ Enable Rediscovery?] [❌ No Thanks]
- **THEN** bot confirms with "You're all set! Try /grateful to write your first entry."

### Requirement: Bot stores user preferences
The system SHALL store user preferences (timezone, digest toggles, rediscovery toggle) in Supabase PostgreSQL.

#### Scenario: User completes onboarding
- **WHEN** onboarding completes
- **THEN** a `user_preferences` record is created with user's Telegram chat_id, timezone, digest_enabled flags, and rediscovery_enabled flag

### Requirement: User can change timezone after onboarding
The system SHALL allow the user to change their timezone at any time via `/timezone <zone>` or through `/settings`.

#### Scenario: User changes timezone
- **WHEN** user sends `/timezone UTC-5`
- **THEN** bot updates the `timezone` field in user_preferences and confirms

### Requirement: User can toggle digest/rediscovery preferences after onboarding
The system SHALL allow the user to enable or disable any digest cadence or rediscovery via `/settings` inline toggles.

#### Scenario: User disables weekly digest
- **WHEN** user taps ❌ on Weekly Digest in /settings
- **THEN** bot updates `digest_weekly_enabled` to false and shows the updated preferences
