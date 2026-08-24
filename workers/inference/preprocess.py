"""Text cleaning before GoEmotions.

Truncation: source mentions 512 and truncation=True but does not settle
characters vs tokens. When a tokenizer is supplied we use Hugging Face
token convention (truncation=True, max_length=512). Character slice is
only a fallback when the tokenizer is unavailable — not the source rule.
"""

from __future__ import annotations

import re
from typing import Any, Protocol

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")
# IMPLEMENTATION: drop leftover URL punctuation / control chars only.
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

HF_MAX_LENGTH = 512


class Tokenizer(Protocol):
    def encode(self, text: str, *, truncation: bool, max_length: int) -> list[int]: ...

    def decode(self, ids: list[int], *, skip_special_tokens: bool) -> str: ...


def preprocess(raw_text: str | None) -> str:
    text = CONTROL_RE.sub(" ", raw_text or "")
    text = URL_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def truncate_for_model(text: str, tokenizer: Tokenizer | None = None) -> str:
    if not text:
        return ""
    if tokenizer is not None:
        ids = tokenizer.encode(text, truncation=True, max_length=HF_MAX_LENGTH)
        return tokenizer.decode(ids, skip_special_tokens=True)
    # IMPLEMENTATION fallback — not a confirmed character-length contract.
    return text[:HF_MAX_LENGTH]


def tokenizer_from_optional(obj: Any) -> Tokenizer | None:
    encode = getattr(obj, "encode", None)
    decode = getattr(obj, "decode", None)
    if callable(encode) and callable(decode):
        return obj
    return None
