import json
import logging
from datetime import date

from scheduler.common.models import GratitudeEntry, User
from scheduler.common.summarizer import DigestSummarizer

logger = logging.getLogger(__name__)

_TYPE_LABELS = {
    "weekly": "this week",
    "monthly": "this month",
    "yearly": "this year",
}


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

        try:
            bedrock_result = await self._call_bedrock(user, digest_type, highlights)
            intro = bedrock_result.get("intro", self._fallback_intro(user, digest_type, highlights))
            annotations = bedrock_result.get("annotations", {})
            body_text = self._annotate_body(body_text, entries_data, annotations)
        except Exception:
            logger.exception("Bedrock summarization failed, falling back to local")
            intro = self._fallback_intro(user, digest_type, highlights)

        return {
            "intro": intro,
            "body": body_text,
            "entries": entries_data,
            "entry_count": len(highlights),
        }

    async def _call_bedrock(
        self,
        user: User,
        digest_type: str,
        highlights: list[GratitudeEntry],
    ) -> dict:
        import boto3

        client = boto3.client("bedrock-runtime")
        prompt = self._build_prompt(user, digest_type, highlights)

        response = client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 300,
                    "temperature": 0.7,
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                }
            ),
        )
        result = json.loads(response["body"].read())
        content = result["content"][0]["text"]

        return self._parse_response(content)

    def _build_prompt(
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
            f"Write a 2-3 sentence warm, personal intro paragraph. "
            f"Identify 1-2 dominant themes. "
            f"Annotate each entry with a short 2-3 word label\n"
            f"(examples: 'most heartfelt', 'rare topic', 'new person').\n\n"
            f"User: {name}\n"
            f"Period: {period}\n"
            f"Entries:\n{entries_text}\n\n"
            "Return ONLY valid JSON, no markdown wrapping:\n"
            '{"intro": "...", "themes": ["...", "..."], '
            '"annotations": {"entry_id1": "label1", "entry_id2": "label2"}}'
        )

    def _parse_response(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
            text = text.strip()
            if text.startswith("json"):
                text = text[4:].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse Bedrock response as JSON")
            return {}

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
        return [
            {
                "id": str(e.id),
                "content": e.content,
                "date": e.created_at.strftime("%Y-%m-%d %H:%M"),
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
        labels = {
            "weekly": "\U0001f4c5 Your Weekly Digest",
            "monthly": "\U0001f4c5 Your Monthly Digest",
            "yearly": "\U0001f4c5 Your Yearly Digest",
        }
        header = labels.get(digest_type, "\U0001f4c5 Your Digest")
        lines = [f"{header} ({period_start} \u2014 {period_end})"]
        for i, entry in enumerate(highlights, 1):
            lines.append(f"\n{i}\u20e3 {entry.content}")
            date_str = entry.created_at.strftime("%Y-%m-%d %H:%M")
            if entry.starred:
                date_str += " \u2b50"
            lines.append(f"   \u2014 {date_str}")
        return "\n".join(lines)

    def _annotate_body(
        self,
        body_text: str,
        entries_data: list[dict],
        annotations: dict,
    ) -> str:
        if not annotations:
            return body_text
        result = body_text
        for entry in entries_data:
            label = annotations.get(entry["id"], "")
            if label:
                result = result.replace(
                    entry["content"],
                    f"{entry['content']} \u2014 {label}",
                )
        return result
