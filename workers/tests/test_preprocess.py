from workers.inference.preprocess import preprocess, truncate_for_model


class FakeTokenizer:
    def encode(self, text: str, *, truncation: bool, max_length: int) -> list[int]:
        _ = truncation
        tokens = list(range(min(len(text), max_length)))
        return tokens

    def decode(self, ids: list[int], *, skip_special_tokens: bool) -> str:
        _ = skip_special_tokens
        return "x" * len(ids)


def test_preprocess_strips_urls_and_whitespace() -> None:
    text = preprocess("  hello   https://example.com/path  world  ")
    assert text == "hello world"
    assert "http" not in text


def test_preprocess_empty() -> None:
    assert preprocess("   ") == ""
    assert preprocess(None) == ""


def test_truncate_uses_tokenizer_max_length() -> None:
    long_text = "a" * 800
    truncated = truncate_for_model(long_text, FakeTokenizer())
    assert len(truncated) == 512


def test_truncate_character_fallback_is_implementation() -> None:
    truncated = truncate_for_model("b" * 600, tokenizer=None)
    assert truncated == "b" * 512
