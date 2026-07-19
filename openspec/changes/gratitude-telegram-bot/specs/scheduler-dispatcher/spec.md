## ADDED Requirements

### Requirement: EventBridge triggers Scheduler Lambda with typed payloads
The system SHALL use AWS EventBridge rules to trigger the Scheduler Lambda. Each trigger SHALL include a JSON payload with a `type` field identifying the task: `reminder`, `weekly`, `monthly`, `yearly`, or `rediscovery`.

#### Scenario: Weekly digest triggered by EventBridge
- **WHEN** EventBridge fires the weekly digest rule (every Sunday at configured time)
- **THEN** Scheduler Lambda receives `{"type": "weekly"}` and executes weekly digest logic

#### Scenario: Reminder triggered by EventBridge
- **WHEN** EventBridge fires the reminder rule (daily)
- **THEN** Scheduler Lambda receives `{"type": "reminder"}` and executes reminder logic

### Requirement: Scheduler Lambda queries eligible users by timezone
The system SHALL query the `user_preferences` table for users whose timezone's current local time falls within the active window for that task type. For reminders and digests, the active window is 7-9pm. For rediscovery, it is 9am-9pm.

#### Scenario: Scheduler filters users by timezone window
- **WHEN** Scheduler Lambda receives a reminder task at 12:00 UTC
- **THEN** it queries users where current local time is 7-9pm (e.g., UTC+8 users at 20:00)
- **THEN** only eligible users receive the reminder

### Requirement: Scheduler Lambda calls Telegram Bot API to send messages
After generating message content, the Scheduler Lambda SHALL call `https://api.telegram.org/bot<TOKEN>/sendMessage` with the user's `chat_id` and message text. For entries requiring inline buttons, it SHALL include an inline keyboard markup.

#### Scenario: Scheduler sends digest via Telegram API
- **WHEN** digest content is ready for a user
- **THEN** Scheduler calls Telegram API with chat_id, message text, and inline keyboard markup for ⭐ Star buttons

### Requirement: Scheduler Lambda handles failures gracefully
If the Telegram API returns an error for a specific user (e.g., user blocked the bot), the Scheduler Lambda SHALL log the error and continue processing remaining users. It SHALL NOT retry failed sends automatically (relies on next cycle).

#### Scenario: User blocked the bot
- **WHEN** Scheduler attempts to send a message
- **AND** Telegram API returns 403 Forbidden
- **THEN** Lambda logs "User <id> has blocked the bot" and continues
