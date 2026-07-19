## Purpose

Define the scheduled digest delivery — weekly, monthly, and yearly reflections.

## Requirements

### Requirement: Weekly digest is sent on Sunday evening
The system SHALL send a weekly digest every Sunday during the user's evening window (7-9pm local time) if the user has weekly digest enabled. The digest SHALL contain highlights from Monday through Sunday of that week.

#### Scenario: User receives weekly digest
- **WHEN** scheduler Lambda runs weekly digest task
- **AND** user has `digest_weekly_enabled` set to true
- **AND** current local time is in user's evening window
- **THEN** bot queries entries from Monday 00:00 to Sunday 23:59 (user's local week)
- **THEN** bot applies highlight selection to pick 3-5 entries
- **THEN** bot sends a message with the selected entries and [⭐ Star] buttons

### Requirement: Monthly digest is sent on the last day of the month
The system SHALL send a monthly digest on the last calendar day of each month during the user's evening window if monthly digest is enabled. The digest SHALL contain highlights from that month.

#### Scenario: User receives monthly digest
- **WHEN** scheduler Lambda runs monthly digest task
- **AND** user has `digest_monthly_enabled` set to true
- **AND** current local time is in user's evening window
- **THEN** bot queries entries from the 1st to the last day of the month
- **THEN** bot applies highlight selection to pick 5-8 entries
- **THEN** bot sends a message with the selected entries and [⭐ Star] buttons

### Requirement: Yearly digest is sent on December 31
The system SHALL send a yearly digest on December 31 during the user's evening window if yearly digest is enabled. The digest SHALL contain highlights from the entire calendar year.

#### Scenario: User receives yearly digest
- **WHEN** scheduler Lambda runs yearly digest task
- **AND** user has `digest_yearly_enabled` set to true
- **AND** current local time is in user's evening window
- **THEN** bot queries entries from January 1 to December 31 of that year
- **THEN** bot applies highlight selection to pick 8-12 entries
- **THEN** bot sends a message with the selected entries and [⭐ Star] buttons
