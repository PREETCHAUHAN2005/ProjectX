from workers.inference.keyword_topics import KeywordTopicClusterer
from workers.inference.lexicon_emotions import LexiconEmotionInferencer
from workers.inference.polarity import GO_EMOTIONS_LABELS, polarity_from_emotions


def test_lexicon_returns_28_labels_and_maps_fear() -> None:
    inferencer = LexiconEmotionInferencer()
    emotions = inferencer.infer("Malware phishing threat after the flood in Assam")
    assert [item.label for item in emotions] == list(GO_EMOTIONS_LABELS)
    assert max(emotions, key=lambda item: item.score).label == "fear"
    polarity, _score = polarity_from_emotions(emotions)
    assert polarity == "NEGATIVE"


def test_lexicon_maps_gratitude() -> None:
    emotions = LexiconEmotionInferencer().infer("Thank you, we are grateful for the restored power")
    assert max(emotions, key=lambda item: item.score).label == "gratitude"
    polarity, _score = polarity_from_emotions(emotions)
    assert polarity == "POSITIVE"


def test_keyword_topics_flood_and_cyber() -> None:
    clusterer = KeywordTopicClusterer()
    flood = clusterer.assign("NDRF boats for flood relief in Patna #floodrelief")
    cyber = clusterer.assign("phishing malware against a civic portal")
    assert flood is not None
    assert flood.topic_name == "flood relief"
    assert cyber is not None
    assert cyber.topic_name == "cyber threat"
    packed = clusterer.assign("malware phishing ransomware credential stuffing")
    assert packed is not None
    assert packed.topic_name == "cyber threat"
