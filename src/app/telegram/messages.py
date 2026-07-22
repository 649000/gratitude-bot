"""User-facing message strings for the Gratitude Bot.

All handler text goes through this module so tone and wording
stay consistent and easy to audit.
"""

import re
from datetime import timedelta

# ── Brand emoji ──────────────────────────────────
EMOJI_JAR = "\U0001fad9"
EMOJI_SPARKLES = "\u2728"
EMOJI_GIFT = "\U0001f381"
EMOJI_STAR = "\u2b50"
EMOJI_DELETE = "\U0001f5d1"
EMOJI_EARTH = "\U0001f30f"
EMOJI_CLOCK = "\U0001f570\ufe0f"
EMOJI_WRITING = "\U0001f4dd"
EMOJI_CALENDAR = "\U0001f4c5"
EMOJI_SMILE = "\U0001f642"
EMOJI_THINKING = "\U0001f914"
EMOJI_GHOST = "\U0001f47b"
EMOJI_PACKAGE = "\U0001f4e6"
EMOJI_WRENCH = "\U0001f6e0\ufe0f"
EMOJI_WAVE = "\U0001f44b"
EMOJI_SMILE_EYES = "\U0001f60a"
EMOJI_GEAR = "\u2699\ufe0f"
EMOJI_SAVED = "\u2728"
EMOJI_LOCATION = "\U0001f4cd"
EMOJI_CHECK = "\u2705"
EMOJI_CROSS = "\u274c"
EMOJI_ALARM = "\u23f0"
EMOJI_PREV = "\u25c0\ufe0f"
EMOJI_NEXT = "\u25b6\ufe0f"
EMOJI_OPEN_BOOK = "\U0001f4d6"
EMOJI_HOURGLASS = "\u231b"
EMOJI_FIRE = "\U0001f525"
EMOJI_CHART = "\U0001f4ca"

# ── Welcome / Onboarding ─────────────────────────
ONBOARD_INTRO = (
    f"Hey {{name}}! {EMOJI_WAVE}\n\n"
    f"I'm your Gratitude Jar {EMOJI_JAR} \u2014 a little space "
    f"to capture moments you're thankful for.\n\n"
    f"Each evening I'll check in and ask about your day. "
    f"On Sundays I'll send a weekly recap, at month-end a monthly one, "
    f"and on Dec 31st your year in gratitude. "
    f"I'll also surprise you with old entries "
    f"you might have forgotten \u2014 like finding a note in a jar.\n\n"
    f"Ready? First, let me know your timezone "
    f"so I reach you at the right times \U0001f447"
)
WELCOME_BACK = (
    f"Welcome back, {{name}}! {EMOJI_JAR}\n\n"
    f"{EMOJI_WRITING} {{count}} entries so far\n"
    f"{EMOJI_FIRE} {{streak}}-day streak\n\n"
    f"Use /grateful to add another, /entries to browse, or /stats to see more."
)
ONBOARD_LOCATION_PROMPT = (
    f"Use the {EMOJI_LOCATION} attachment menu to share your location "
    f"and I'll detect your timezone.\n\nOr use /timezone to set it manually."
)
ONBOARD_PREFS_EXPLAINER = (
    f"Got it! Your timezone is {{tz}} {EMOJI_CLOCK}"
    f"\n\nNow let me show you what I can do. "
    f"You can toggle any of these later in /settings:\n\n"
    f"{EMOJI_ALARM} Evening Reminder \u2014 I'll check in each evening (7\u20139pm) "
    f"if you haven't written yet\n"
    f"{EMOJI_CALENDAR} Weekly Digest \u2014 Every Sunday, your week's highlights\n"
    f"{EMOJI_CALENDAR} Monthly Digest \u2014 A recap at the end of each month\n"
    f"{EMOJI_CALENDAR} Yearly Digest \u2014 Your year in gratitude, on Dec 31st\n"
    f"{EMOJI_GIFT} Rediscovery \u2014 A few times a week, "
    f"I'll surprise you with a random past entry\n\n"
    f"Ready to enable all of them?"
)
ONBOARD_ALL_DONE = (
    f"All set! {EMOJI_SPARKLES}\n\n"
    f"Just send me anything you're grateful for, anytime. For example:\n\n"
    f"'Grateful for the morning coffee \u2615'\n"
    f"'My team was amazing today'\n"
    f"'Had a great walk in the park'\n\n"
    f"Your first entry is just a message away. "
    f"Got something in mind already?"
)
ONBOARD_SIMPLE_DONE = ONBOARD_ALL_DONE
PREF_TOGGLE_PROMPT = f"Tap to toggle \u2014 I'll wait {EMOJI_SMILE_EYES}\n"
PREF_CHOOSE_PROMPT = "Tap to toggle each preference:\n"

# ── Timezone ────────────────────────────────────
TZ_SELECT = f"What timezone are you in? {EMOJI_EARTH}"
TZ_SET = f"Got it! Your timezone is {{tz}} {EMOJI_CLOCK}"
TZ_UPDATED = f"Timezone updated to {{tz}} {EMOJI_CLOCK}"
TZ_USAGE = f"Try: /timezone UTC+8\n\nI understand UTC-12 to UTC+12 {EMOJI_SMILE}"
TZ_INVALID = "Hmm, I don't recognise '{tz_input}'. Try something like UTC+8, UTC-5, or UTC."
TZ_PROMPT = (
    f"Your timezone is currently {{tz}} {EMOJI_CLOCK}\n\n"
    f"Pick an option below, or type /timezone UTC+8"
)
TZ_COMMON_OFFSETS = [
    ("UTC-8 (PST)", "UTC-8"),
    ("UTC-5 (EST)", "UTC-5"),
    ("UTC", "UTC"),
    ("UTC+1 (CET)", "UTC+1"),
    ("UTC+3 (MSK)", "UTC+3"),
    ("UTC+5:30 (IST)", "UTC+5:30"),
    ("UTC+7 (ICT)", "UTC+7"),
    ("UTC+8 (SGT)", "UTC+8"),
]

# ── Gratitude Entry ──────────────────────────────
ENTRY_SAVED_RESPONSES = [
    f"Lovely! Added to your jar {EMOJI_JAR}",
    f"Beautiful! Now in your jar {EMOJI_SPARKLES}",
    "Noted with gratitude \U0001f4ab",
    f"That's a keeper! Saved {EMOJI_JAR}",
    "Wonderful moment \u2014 saved! \U0001f31f",
    f"Your jar just got a little fuller {EMOJI_JAR}",
]
ENTRY_TOO_SHORT = (
    f"That's a bit short for a gratitude! What are you grateful for today? {EMOJI_WRITING}"
)

# ── Entries / Jar Browsing ───────────────────────
JAR_EMPTY = f"Your jar is empty! Start filling it with /grateful {EMOJI_JAR}{EMOJI_SPARKLES}"
NO_ENTRIES_PERIOD = f"No entries in {{period}} yet \u2014 time to build a streak? {EMOJI_WRITING}"
NO_MORE_ENTRIES = f"That's your whole jar for this period! {EMOJI_JAR}"
YEAR_SELECT = f"{EMOJI_CALENDAR} Select a year:"
MONTH_SELECT = f"{EMOJI_CALENDAR} Select a month in {{year}}:"
ENTRIES_HEADER = f"{EMOJI_OPEN_BOOK} {{label}} ({{count}} entries):\n\n"
ENTRIES_PAGE_HEADER = (
    f"{EMOJI_OPEN_BOOK} {{label}} ({{count}} entries)"
    f" \u2014 page {{page}}/{{pages}}:\n\n"
)

# ── Surprise / Rediscovery ───────────────────────
SURPRISE_PREFIX = f"{EMOJI_GIFT} Here's a surprise from your jar:\n\n"

# ── Export ───────────────────────────────────────
EXPORT_EMPTY = f"Your jar is empty. Write something first with /grateful {EMOJI_JAR}"
EXPORT_SUCCESS = (
    f"{EMOJI_PACKAGE} {{count}} moments of gratitude exported. Keep filling that jar! {EMOJI_JAR}"
)

# ── Settings ────────────────────────────────────
SETTINGS_HEADER = f"{EMOJI_GEAR} Your preferences:"
TOGGLE_REMINDER = "Daily Reminder"
TOGGLE_WEEKLY = "Weekly Digest"
TOGGLE_MONTHLY = "Monthly Digest"
TOGGLE_YEARLY = "Yearly Digest"
TOGGLE_REDISCOVERY = "Rediscovery"
TOGGLE_TIMEZONE = "Timezone: {tz}"

# ── Callbacks / Actions ─────────────────────────
ENTRY_REMOVED = f"Entry removed {EMOJI_DELETE}"
ENTRY_VANISHED = f"This entry seems to have vanished {EMOJI_GHOST}"
STARRED = f"{EMOJI_STAR} Starred!"
UNSTARRED = "Unstarred"

# ── Negative Scenarios ──────────────────────────
UNKNOWN_COMMAND = f"I don't know that command! Try /help to see what I can do {EMOJI_SMILE}"
NOT_TEXT_MESSAGE = f"I only understand text for now. Try /grateful to write an entry! {EMOJI_JAR}"
GENERIC_ERROR = f"Something went wrong on my end. Try again in a moment {EMOJI_WRENCH}"
GENERIC_ERROR_WITH_NOTIFY = f"Oops! Something went wrong. The team has been notified {EMOJI_WRENCH}"

# ── Help ────────────────────────────────────────
HELP_MESSAGE = (
    f"{EMOJI_WAVE} Hey {{name}}! I'm your gratitude jar. Here's what I can do:\n\n"
    f"/grateful \u2014 Write a gratitude entry\n"
    f"/surprise \u2014 Rediscover a random past entry\n"
    f"/entries \u2014 Browse your jar\n"
    f"/star \u2014 See your starred entries\n"
    f"/stats \u2014 See your statistics\n"
    f"/settings \u2014 View and toggle preferences\n"
    f"/timezone \u2014 Change your timezone\n"
    f"/export \u2014 Download all your entries\n"
    f"/help \u2014 Show this message\n\n"
    f"Send me what you're grateful for anytime! {EMOJI_JAR}"
)

# ── Stats ───────────────────────────────────────
STATS_TEMPLATE = (
    f"{EMOJI_CHART} *Your Gratitude Stats*\n\n"
    f"{EMOJI_JAR} Total entries: {{total}}\n"
    f"{EMOJI_WRITING} This week: {{week}}\n"
    f"{EMOJI_CALENDAR} This month: {{month}}\n"
    f"{EMOJI_STAR} Starred: {{starred}}\n"
    f"{EMOJI_FIRE} Current streak: {{streak}} days\n"
    f"{EMOJI_HOURGLASS} Since: {{since}}\n\n"
    f"Keep filling that jar! {EMOJI_JAR}{EMOJI_SPARKLES}"
)

STATS_BTN_ENTRIES = f"{EMOJI_OPEN_BOOK} Browse entries"
STATS_BTN_SETTINGS = f"{EMOJI_GEAR} Settings"

HELP_BTN_GRATEFUL = f"{EMOJI_WRITING} Write an entry"
HELP_BTN_ENTRIES = f"{EMOJI_OPEN_BOOK} Browse my jar"
HELP_BTN_STATS = f"{EMOJI_CHART} My stats"
HELP_BTN_STAR = f"{EMOJI_STAR} Starred entries"
HELP_BTN_SURPRISE = f"{EMOJI_GIFT} Surprise me"
HELP_BTN_SETTINGS = f"{EMOJI_GEAR} Settings"

# ── Starred Entries ──────────────────────────────
STARS_EMPTY = f"No starred entries yet. Star an entry with {EMOJI_STAR} in /entries or /surprise"
STARS_HEADER = f"{EMOJI_STAR} Starred Entries ({{shown}} of {{total}}):\n\n"

# ── Date formatting (shared) ────────────────────
ENTRY_DATE_FORMAT = "%d %b %Y, %-I:%M %p"
DIGEST_DATE_FORMAT = "%d %b %Y"

# ── Fallback prompts ────────────────────────────
FALLBACK_PROMPT = "What are you grateful for today?"


# ── Helpers ─────────────────────────────────────
def _escape_md(text: str) -> str:
    """Escape Telegram MarkdownV1 special characters in inline text."""
    return re.sub(r"([_*\[\]()~`>#+\-=|{}])", r"\\\1", text)


def _parse_utc_offset_minutes(tz_str: str) -> int:
    if tz_str == "UTC":
        return 0
    offset = tz_str[3:]
    if ":" in offset:
        hours_str, minutes_str = offset.split(":")
        hours = int(hours_str)
        minutes = int(minutes_str)
        return hours * 60 + (minutes if hours >= 0 else -minutes)
    return int(offset) * 60


def format_entry_date(dt):
    """Format a datetime for user display: '21 Jul 2023, 2:41 PM'."""
    return dt.strftime(ENTRY_DATE_FORMAT)


def format_entry_date_local(dt, tz_str: str) -> str:
    """Format a datetime in the user's timezone."""
    offset_minutes = _parse_utc_offset_minutes(tz_str)
    local_dt = dt + timedelta(minutes=offset_minutes)
    return local_dt.strftime(ENTRY_DATE_FORMAT)


def format_entry_date_short(dt, tz_str: str) -> str:
    """Format a date for day headers: 'Wed 15 Jul'."""
    offset_minutes = _parse_utc_offset_minutes(tz_str)
    local_dt = dt + timedelta(minutes=offset_minutes)
    return local_dt.strftime("%a %d %b")


def format_digest_date(dt):
    """Format a date for digest headers: '21 Jul 2023'."""
    return dt.strftime(DIGEST_DATE_FORMAT)
