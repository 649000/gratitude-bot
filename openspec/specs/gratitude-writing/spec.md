## Purpose

Define how users write gratitude entries and how the bot prompts and reminds them.

## Requirements

### Requirement: User writes entries via /grateful
The system SHALL allow users to write gratitude entries by initiating `/grateful`, receiving a random prompt, and replying with free text.

#### Scenario: User writes an entry
- **WHEN** user sends `/grateful`
- **THEN** bot sends a random prompt from the `prompts` table
- **WHEN** user replies with text
- **THEN** bot saves the entry with user_id, message text, and UTC timestamp
- **THEN** bot replies "✨ Saved!"

### Requirement: Prompts are stored in a database table
The system SHALL store prompts in a `prompts` table with `id`, `text`, and `category` fields. Prompts SHALL be selectable at random.

#### Scenario: Bot selects a random prompt
- **WHEN** user sends `/grateful`
- **THEN** bot queries `SELECT text FROM prompts ORDER BY RANDOM() LIMIT 1`

### Requirement: Evening reminders nudge users to write
The system SHALL send a reminder message during the user's evening window (7-9pm local time) ONLY if the user has not written any entry that calendar day (in their local timezone) AND has reminders enabled in preferences.

#### Scenario: User hasn't written today — gets reminder
- **WHEN** scheduler Lambda runs the reminder task for a user
- **AND** user has no entries with `created_at` matching today's local date
- **AND** user has reminders enabled
- **THEN** bot sends "How was your day? 🫙" with a random prompt

#### Scenario: User already wrote today — no reminder
- **WHEN** scheduler Lambda runs the reminder task
- **AND** user has at least one entry from today (local date)
- **THEN** bot does NOT send a reminder
