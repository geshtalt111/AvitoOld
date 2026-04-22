import json
from urllib import error, request

from django.conf import settings


PHONE_ASSISTANT_SYSTEM_PROMPT = """
You are a helpful universal AI assistant.
Always reply in Russian unless the user explicitly asks for another language.
Answer any user question as clearly and practically as possible.
If something is uncertain, say so honestly instead of inventing facts.
Prefer concise, structured answers that are easy to read.
""".strip()


class PhoneAssistantError(Exception):
    pass


class PhoneAssistantConfigurationError(PhoneAssistantError):
    pass


def _extract_error_message(raw_payload):
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError:
        return "Сервис помощника сейчас недоступен."

    if isinstance(payload, dict):
        error_block = payload.get("error")
        if isinstance(error_block, dict):
            return error_block.get("message") or "Сервис помощника сейчас недоступен."
        if isinstance(error_block, str):
            return error_block

    return "Сервис помощника сейчас недоступен."


def _extract_reply_text(content):
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item.strip())
                continue

            if not isinstance(item, dict):
                continue

            text = item.get("text") or item.get("content")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())

        return "\n".join(part for part in parts if part).strip()

    return ""


def ask_phone_assistant(messages):
    if not settings.AI_API_KEY:
        raise PhoneAssistantConfigurationError("Ключ AI API не настроен.")

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": PHONE_ASSISTANT_SYSTEM_PROMPT,
            },
            *messages,
        ],
        "temperature": 0.5,
        "max_tokens": 500,
    }

    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    if "openrouter.ai" in settings.AI_API_URL:
        headers["HTTP-Referer"] = settings.AI_SITE_URL
        headers["X-OpenRouter-Title"] = settings.AI_APP_NAME

    api_request = request.Request(
        settings.AI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=45) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw_payload = exc.read().decode("utf-8", errors="ignore")
        message = _extract_error_message(raw_payload)
        raise PhoneAssistantError(message) from exc
    except error.URLError as exc:
        raise PhoneAssistantError("Не удалось подключиться к сервису помощника.") from exc
    except json.JSONDecodeError as exc:
        raise PhoneAssistantError("Сервис помощника вернул непонятный ответ.") from exc

    choices = response_payload.get("choices") or []
    if not choices:
        raise PhoneAssistantError("Сервис помощника не вернул ответ.")

    assistant_message = choices[0].get("message") or {}
    reply = _extract_reply_text(assistant_message.get("content"))
    if not reply:
        raise PhoneAssistantError("Сервис помощника вернул пустой ответ.")

    return reply, response_payload.get("model") or settings.AI_MODEL
