# pii_redaction.py
"""
PII Redaction for Observability
Required for GDPR, HIPAA, SOC2 compliance
"""

import re
import os
from dotenv import load_dotenv

from langfuse import observe, get_client, propagate_attributes
import anthropic

from common import print_section

load_dotenv()
PROJECT_NAME = "PII Redaction for Observability"

class PIIRedactor:
    """Redact PII before logging to observability platform."""

    SECRET_ENV_MARKERS = (
        "API_KEY",
        "TOKEN",
        "SECRET",
        "PASSWORD",
        "PRIVATE_KEY",
    )

    PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        # Matches labeled secrets and common provider-specific key prefixes.
        "api_key": (
            r"(?i)\b(?:api[_ -]?key|access[_ -]?token|secret[_ -]?key)"
            r"\s*(?:is|:|=)\s*['\"]?[A-Za-z0-9_&/\-]{16,}['\"]?"
            r"|\b(?:LLM_|sk-ant-api\d{2}-|sk-|AIza|xox[baprs]-|gh[pousr]_)"
            r"[A-Za-z0-9_&/\-]{16,}\b"
        ),
    }

    def __init__(self) -> None:
        """Cache configured secret values for exact-value redaction."""
        self.secret_values = tuple(
            value
            for name, value in os.environ.items()
            if any(marker in name.upper() for marker in self.SECRET_ENV_MARKERS)
            and len(value) >= 8
        )

    def redact(self, text: str) -> str:
        """Redact all PII patterns from text."""
        result = text
        for pii_type, pattern in self.PATTERNS.items():
            result = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", result)
        for secret in self.secret_values:
            result = result.replace(secret, "[REDACTED_API_KEY]")
        return result

    def redact_dict(self, data: dict) -> dict:
        """Recursively redact PII from a dictionary."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.redact(value)
            elif isinstance(value, dict):
                result[key] = self.redact_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self.redact(v) if isinstance(v, str) else v for v in value
                ]
            else:
                result[key] = value
        return result


@observe(
    name="Claude-generation",
    as_type="generation",
    capture_input=False,
    capture_output=False,
)
def secure_call_claude(prompt: str) -> str:
    """Call Claude API and record it as a Langfuse generation.

    Claude responses can contain thinking blocks before the text block, so the
    first content item must not be assumed to have a ``text`` attribute.
    """

    client = anthropic.Anthropic()
    model = "claude-haiku-5-5"
    messages = [{"role": "user", "content": prompt}]

    # Keep PII out of Langfuse while sending the original prompt to Claude.
    traced_messages = [{"role": "user", "content": redactor.redact(prompt)}]
    langfuse.update_current_generation(
        input=traced_messages,
        model=model,
        model_parameters={"max_tokens": 1024},
    )

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=messages,
    )
    text = "".join(
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    )
    if not text:
        raise RuntimeError("Claude returned no text content")

    langfuse.update_current_generation(
        model=response.model,
        output=redactor.redact(text),
        usage_details={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        },
    )
    return text


# Integrate with your observability


langfuse = get_client()
redactor = PIIRedactor()


@observe(capture_input=False, capture_output=False)
def secure_llm_call(prompt: str) -> str:
    """LLM call with PII redaction for logs.

    Note: We disable automatic capture and manually log redacted versions.
    """

    response = secure_call_claude(prompt)

    # Manually log redacted versions using v4 API
    langfuse.update_current_span(
        input=redactor.redact(prompt),
        output=redactor.redact(response),
    )

    return response


if __name__ == "__main__":
    print_section("🔒 Testing PII Redaction for Observability")

    # Test with a prompt containing PII
    test_prompt = """
    Please help me with my account. My email is john.doe@example.com
    and my phone number is 555-123-4567. My SSN is 123-45-6789. My LLM Api key is LLM_11341512812334_yEasbceN_tst&M6_4asbdddoAxk
    """
    with propagate_attributes(
        user_id="user_123",
        tags=["pii-redaction", "pii-redaction"],
        metadata={"project": PROJECT_NAME},
    ):
        result = secure_llm_call(test_prompt)
        print(f"Response: {result}")
    langfuse.flush()
