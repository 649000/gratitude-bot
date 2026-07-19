## Purpose

Define how users rediscover past entries — both automated and on-demand.

## Requirements

### Requirement: Bot sends random rediscoveries during user daytime
The system SHALL send a random past gratitude entry to the user approximately 4-6 times per week during their daytime window (9am-9pm local time) if rediscovery is enabled. Intervals SHALL be unpredictable.

#### Scenario: User receives a rediscovery
- **WHEN** scheduler Lambda runs rediscovery task for a user
- **AND** user has `rediscovery_enabled` set to true
- **AND** current local time is within the user's allowed window
- **THEN** bot selects a random entry from the user's full entry history
- **THEN** bot sends the entry with [⭐ Star] [🗑 Delete] inline buttons

### Requirement: Rediscovery respects user's daytime window and avoids clustered sends
The system SHALL schedule rediscoveries with random intervals and SHALL NOT send more than once within a configurable cooldown period (default: minimum 4 hours between rediscoveries for the same user).

#### Scenario: Rediscovery cooldown prevents duplicate sends
- **WHEN** scheduler Lambda checks a user for rediscovery
- **AND** the user received a rediscovery less than 4 hours ago
- **THEN** bot skips sending and tries again later

### Requirement: /surprise on-demand rediscovery
The system SHALL also provide `/surprise` as an on-demand command that works identically to one rediscovery event (see `telegram-bot-commands` spec for command details).
