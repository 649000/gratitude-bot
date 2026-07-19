## Purpose

Define the Telegram bot command handlers that users interact with directly.

## Requirements

### Requirement: Bot responds to /grateful command
The system SHALL respond to the `/grateful` command by sending a random prompt from the prompts table, then saving the user's free-form text reply as a new gratitude entry.

#### Scenario: User sends /grateful and writes an entry
- **WHEN** user sends `/grateful`
- **THEN** bot replies with a random prompt (e.g., "What made you smile today?")
- **WHEN** user replies with free text
- **THEN** bot saves the entry with user_id, message text, and current timestamp, and replies with "✨ Saved!"

### Requirement: Bot responds to /surprise command
The system SHALL respond to the `/surprise` command by selecting a random past entry from the user's jar and sending it with inline ⭐ Star and 🗑 Delete buttons.

#### Scenario: User sends /surprise with existing entries
- **WHEN** user sends `/surprise`
- **THEN** bot queries all entries for that user, selects one at random, and sends it as a message with [⭐ Star] [🗑 Delete] inline buttons

#### Scenario: User sends /surprise with no entries
- **WHEN** user sends `/surprise` and has no entries
- **THEN** bot replies "Your jar is empty! Write your first entry with /grateful 🫙"

### Requirement: Bot responds to /entries command
The system SHALL respond to `/entries` with an interactive drill-down (year → month → day/all), and to `/entries YYYY`, `/entries YYYY-MM`, and `/entries YYYY-MM-DD` with the corresponding view. Paginated lists SHALL use ◀️ ▶️ inline buttons.

#### Scenario: User sends /entries without arguments
- **WHEN** user sends `/entries`
- **THEN** bot replies with inline year buttons for all years containing entries

#### Scenario: User sends /entries 2026-07
- **WHEN** user sends `/entries 2026-07`
- **THEN** bot shows entries from July 2026 with [◀️] [▶️] pagination if more than 5 entries

#### Scenario: User sends /entries 2026-07-17
- **WHEN** user sends `/entries 2026-07-17`
- **THEN** bot shows all entries from that date

### Requirement: Bot responds to /settings command
The system SHALL show the user's current preferences with inline toggle buttons for each digest cadence and rediscovery, plus a timezone option.

#### Scenario: User sends /settings
- **WHEN** user sends `/settings`
- **THEN** bot shows current preferences with [✅/❌] toggle buttons for daily reminder, weekly digest, monthly digest, yearly digest, and rediscovery, plus [📍 Change Timezone]

### Requirement: Bot responds to /export command
The system SHALL return all of the user's entries as a downloadable file (`.txt` or `.json`).

#### Scenario: User sends /export
- **WHEN** user sends `/export`
- **THEN** bot sends a file containing all entries with date, time, and message text

### Requirement: Bot responds to /help command
The system SHALL list all available commands with brief descriptions.

#### Scenario: User sends /help
- **WHEN** user sends `/help`
- **THEN** bot replies with a list of commands: /grateful, /surprise, /entries, /settings, /export, /timezone, /help

### Requirement: Bot responds to /timezone command
The system SHALL allow the user to set their timezone manually via `/timezone <zone>`.

#### Scenario: User sends /timezone UTC+8
- **WHEN** user sends `/timezone UTC+8`
- **THEN** bot updates their timezone preference and confirms with "Timezone set to UTC+8"

### Requirement: Bot handles inline button callbacks
The system SHALL process inline button callbacks: ⭐ Star (marks entry as starred), 🗑 Delete (removes entry), ◀️ ▶️ (navigates paginated lists), and preference toggles (enables/disables settings).

#### Scenario: User taps ⭐ Star
- **WHEN** user taps the ⭐ Star inline button
- **THEN** bot updates the entry's `starred` flag to true and replies with "⭐ Starred!"

#### Scenario: User taps 🗑 Delete
- **WHEN** user taps the 🗑 Delete inline button
- **THEN** bot deletes the entry and replies with "🗑 Deleted"
