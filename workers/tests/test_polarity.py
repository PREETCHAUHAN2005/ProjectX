from workers.inference.polarity import EmotionScore, polarity_from_emotions


def _score(label: str, value: float) -> EmotionScore:
    return EmotionScore(label, value)


def test_joy_maps_positive() -> None:
    emotions = [_score("joy", 0.8), _score("neutral", 0.1), _score("anger", 0.05)]
    label, score = polarity_from_emotions(emotions)
    assert label == "POSITIVE"
    assert score == 0.8


def test_love_maps_positive() -> None:
    emotions = [_score("love", 0.7), _score("sadness", 0.2)]
    label, _score_value = polarity_from_emotions(emotions)
    assert label == "POSITIVE"


def test_fear_maps_negative() -> None:
    emotions = [_score("fear", 0.6), _score("joy", 0.1)]
    label, _ = polarity_from_emotions(emotions)
    assert label == "NEGATIVE"


def test_anger_maps_negative() -> None:
    emotions = [_score("anger", 0.55), _score("neutral", 0.4)]
    label, _ = polarity_from_emotions(emotions)
    assert label == "NEGATIVE"


def test_neutral_dominant_is_neutral() -> None:
    emotions = [_score("neutral", 0.9), _score("joy", 0.05)]
    label, _ = polarity_from_emotions(emotions)
    assert label == "NEUTRAL"


def test_tie_prefers_neutral() -> None:
    emotions = [_score("joy", 0.5), _score("fear", 0.5)]
    label, _ = polarity_from_emotions(emotions)
    assert label == "NEUTRAL"
