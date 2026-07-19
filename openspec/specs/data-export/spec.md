## Purpose

Define how users export their gratitude data.

## Requirements

### Requirement: User can export all entries
The system SHALL allow users to download all their gratitude entries via `/export`. The export SHALL include entry text, date, time, and starred status for each entry.

#### Scenario: User requests export
- **WHEN** user sends `/export`
- **THEN** bot queries all entries for that user, ordered by `created_at` ascending
- **THEN** bot formats entries as a `.txt` or `.json` file
- **THEN** bot sends the file as a Telegram document

#### Scenario: User requests export with no entries
- **WHEN** user sends `/export`
- **AND** user has no entries
- **THEN** bot replies "Your jar is empty. Write something first with /grateful 🫙"
