from datetime import date

from aws_lambda_powertools import Logger

from scheduler.common.models import GratitudeEntry, User
from scheduler.common.summarizer import DigestSummarizer

logger = Logger(service="digest-builder")

_TYPE_LABELS = {
    "weekly": "this week",
    "monthly": "this month",
    "yearly": "this year",
}


_MAX_TOKENS = 5000


class BedrockSummarizer(DigestSummarizer):
    def __init__(self, model_id: str):
        self.model_id = model_id

    async def summarize(
        self,
        user: User,
        digest_type: str,
        period_start: date,
        period_end: date,
        highlights: list[GratitudeEntry],
    ) -> dict:
        entries_data = self._build_entry_list(highlights)
        body_text = self._build_body(digest_type, period_start, period_end, highlights)

        fallback = self._fallback_intro(user, digest_type, highlights)

        try:
            intro_themes = await self._call_intro_themes(user, digest_type, highlights)
            intro = intro_themes.get("intro", fallback)
        except Exception:
            logger.exception("Bedrock intro/themes failed, falling back to local")
            intro = fallback

        try:
            annotation_result = await self._call_annotations(user, digest_type, highlights)
            annotations = annotation_result.get("annotations", [])
            body_text = self._annotate_body(body_text, entries_data, annotations)
        except Exception:
            logger.exception("Bedrock annotations failed, using unannotated body")

        logger.info(
            "Bedrock summarization complete for user %s (model=%s)",
            user.id,
            self.model_id,
        )

        return {
            "intro": intro,
            "body": body_text,
            "entries": entries_data,
            "entry_count": len(highlights),
        }

    def _converse(self, prompt: str, tool_config: dict) -> dict:
        import boto3

        client = boto3.client("bedrock-runtime")

        response = client.converse(
            modelId=self.model_id,
            messages=[
                {"role": "user", "content": [{"text": prompt}]},
            ],
            inferenceConfig={
                "maxTokens": _MAX_TOKENS,
                "temperature": 0.0,
            },
            additionalModelRequestFields={
                "inferenceConfig": {"topK": 1}
            },
            toolConfig=tool_config,
        )

        logger.debug("Bedrock stopReason: %s", response.get("stopReason"))

        for block in response["output"]["message"]["content"]:
            if "toolUse" in block:
                result = block["toolUse"]["input"]
                logger.debug("Raw Bedrock response: %s", result)
                return result

        logger.warning("Bedrock response contained no toolUse block")
        return {}

    async def _call_intro_themes(
        self,
        user: User,
        digest_type: str,
        highlights: list[GratitudeEntry],
    ) -> dict:
        prompt = self._build_intro_themes_prompt(user, digest_type, highlights)

        tool_config = {
            "tools": [{
                "toolSpec": {
                    "name": "write_intro_themes",
                    "description": "Write a gratitude journal intro and identify themes",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "intro": {"type": "string"},
                                "themes": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["intro", "themes"],
                        }
                    }
                }
            }],
            "toolChoice": {"tool": {"name": "write_intro_themes"}},
        }

        return self._converse(prompt, tool_config)

    async def _call_annotations(
        self,
        user: User,
        digest_type: str,
        highlights: list[GratitudeEntry],
    ) -> dict:
        prompt = self._build_annotations_prompt(user, digest_type, highlights)

        tool_config = {
            "tools": [{
                "toolSpec": {
                    "name": "write_annotations",
                    "description": "Annotate each gratitude entry with a short label",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "annotations": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "entry_id": {"type": "string"},
                                            "label": {"type": "string"},
                                        },
                                        "required": ["entry_id", "label"],
                                    },
                                },
                            },
                            "required": ["annotations"],
                        }
                    }
                }
            }],
            "toolChoice": {"tool": {"name": "write_annotations"}},
        }

        return self._converse(prompt, tool_config)

    def _build_intro_themes_prompt(
        self,
        user: User,
        digest_type: str,
        highlights: list[GratitudeEntry],
    ) -> str:
        name = user.first_name or "there"
        period = _TYPE_LABELS.get(digest_type, "recently")

        entries_text = "\n".join(
            f'{i + 1}. "{e.content}"' + (" (starred)" if e.starred else "")
            for i, e in enumerate(highlights)
        )

        return (
            f"You are a digest writer for a gratitude journal Telegram bot. "
            f"Write a 2-3 sentence warm, personal intro paragraph. "
            f"Identify 1-2 dominant themes in these entries.\n\n"
            f"User: {name}\n"
            f"Period: {period}\n"
            f"Entries:\n{entries_text}"
        )

    def _build_annotations_prompt(
        self,
        user: User,
        digest_type: str,
        highlights: list[GratitudeEntry],
    ) -> str:
        name = user.first_name or "there"
        period = _TYPE_LABELS.get(digest_type, "recently")

        entries_text = "\n".join(
            f'{i + 1}. "{e.content}" [id={e.id}]' + (" (starred)" if e.starred else "")
            for i, e in enumerate(highlights)
        )

        return (
            f"You are a digest writer for a gratitude journal Telegram bot. "
            f"Annotate each entry with a short 2-3 word label\n"
            f"(examples: 'most heartfelt', 'rare topic', 'new person').\n\n"
            f"User: {name}\n"
            f"Period: {period}\n"
            f"Entries:\n{entries_text}"
        )

    def _build_intro(
        self,
        user: User,
        digest_type: str,
        _highlights: list[GratitudeEntry],
    ) -> str:
        name = user.first_name or "there"
        period = _TYPE_LABELS.get(digest_type, "recently")
        return f"{name}, here are your highlights from {period} \U0001f4ab"

    def _fallback_intro(
        self,
        user: User,
        digest_type: str,
        _highlights: list[GratitudeEntry],
    ) -> str:
        name = user.first_name or "there"
        period = _TYPE_LABELS.get(digest_type, "recently")
        return f"{name}, here are your highlights from {period} \U0001f4ab"

    def _build_entry_list(self, highlights: list[GratitudeEntry]) -> list[dict]:
        from app.telegram.messages import format_entry_date

        return [
            {
                "id": str(e.id),
                "content": e.content,
                "date": format_entry_date(e.created_at),
                "starred": e.starred,
            }
            for e in highlights
        ]

    def _build_body(
        self,
        digest_type: str,
        period_start: date,
        period_end: date,
        highlights: list[GratitudeEntry],
    ) -> str:
        from app.telegram.messages import format_digest_date, format_entry_date

        labels = {
            "weekly": "\U0001f4c5 Your Weekly Digest",
            "monthly": "\U0001f4c5 Your Monthly Digest",
            "yearly": "\U0001f4c5 Your Yearly Digest",
        }
        header = labels.get(digest_type, "\U0001f4c5 Your Digest")
        lines = [
            f"{header} ({format_digest_date(period_start)} \u2014 {format_digest_date(period_end)})"
        ]
        for i, entry in enumerate(highlights, 1):
            lines.append(f"\n{i}. {entry.content}")
            date_str = format_entry_date(entry.created_at)
            if entry.starred:
                date_str += " \u2b50"
            lines.append(f"   \u2014 {date_str}")
        return "\n".join(lines)

    def _annotate_body(
        self,
        body_text: str,
        entries_data: list[dict],
        annotations: list[dict],
    ) -> str:
        if not annotations:
            return body_text
        result = body_text
        for entry in entries_data:
            label = ""
            for a in annotations:
                if a.get("entry_id") == entry["id"]:
                    label = a.get("label", "")
                    break
            if label:
                result = result.replace(
                    entry["content"],
                    f"{entry['content']} \u2014 {label}",
                )
        return result
