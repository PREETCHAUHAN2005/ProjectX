"""IMPLEMENTATION demo scenario — not live Telegram/X traffic.

A readable flood-relief thread: root posts, comments, GoEmotions labels.
Used when DEMO_SEED=true so the dashboard can be recorded without Redis.
"""

from __future__ import annotations

import logging
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

_ticker: deque[dict[str, Any]] = deque()
_loaded = False

ROOT_IMD = "imd-rain-alert"
ROOT_RELIEF = "relief-camps-open"


def hours_ago(hours: float) -> str:
    stamp = datetime.now(timezone.utc) - timedelta(hours=hours)
    return stamp.replace(microsecond=0).isoformat()


def _emotions(dominant: str, score: float = 0.64) -> list[dict[str, float | str]]:
    second = "neutral" if dominant != "neutral" else "approval"
    third = "fear" if dominant not in {"fear", "neutral"} else "optimism"
    leftover = max(0.0, 1.0 - score)
    return [
        {"label": dominant, "score": round(score, 3)},
        {"label": second, "score": round(leftover * 0.55, 3)},
        {"label": third, "score": round(leftover * 0.45, 3)},
    ]


def _doc(
    *,
    platform: str,
    external_id: str,
    hours: float,
    handle: str,
    user_id: str,
    text: str,
    polarity: str,
    dominant: str,
    topic: str,
    role: str,
    reply_to: str | None = None,
    severity: str = "medium",
    country: str = "India",
    language: str = "English",
    profession: str = "Public sector",
    hashtags: list[str] | None = None,
    score: float = 0.64,
    likes: int | None = None,
) -> dict[str, Any]:
    return {
        "platform": platform,
        "external_id": external_id,
        "timestamp": hours_ago(hours),
        "author": {
            "user_id": user_id,
            "handle": handle,
            "follower_count": 1200,
        },
        "content": {
            "raw_text": text,
            "clean_text": text,
            "hashtags": hashtags or ["floodrelief"],
            "language": language,
        },
        "analytics": {
            "sentiment": {"label": polarity, "score": score},
            "emotions": _emotions(dominant, score),
            "topic_id": topic,
            "topic_name": topic,
            "demographics": {
                "inferred_country": country,
                "inferred_region": None,
                "inferred_profession": profession,
                "confidence": 0.62,
            },
            "thread_role": role,
            "in_reply_to": reply_to,
            "severity": severity,
        },
        "engagement": {"likes": likes, "shares": None, "views": None},
    }


def _unique_thread() -> list[dict[str, Any]]:
    flood = "flood relief"
    power = "power outage"
    air = "air quality"
    return [
        _doc(
            platform="x",
            external_id=ROOT_IMD,
            hours=6.2,
            handle="IndiaMetDept",
            user_id="imd",
            text=(
                "Orange alert: heavy rain over Mumbai and Pune until 10pm IST. "
                "Avoid coastal roads and underpasses. Updates with @MumbaiPolice."
            ),
            polarity="NEGATIVE",
            dominant="fear",
            topic=flood,
            role="post",
            severity="high",
            profession="Public sector",
            likes=1840,
        ),
        _doc(
            platform="telegram",
            external_id=ROOT_RELIEF,
            hours=5.4,
            handle="ReliefOpsIN",
            user_id="reliefops",
            text=(
                "Three relief camps are open at municipal schools in Dadar, Kurla, "
                "and Andheri. Dry rations staged. Coordinating with @IndiaMetDept."
            ),
            polarity="POSITIVE",
            dominant="approval",
            topic=flood,
            role="post",
            severity="medium",
            profession="Public sector",
            likes=920,
        ),
        _doc(
            platform="x",
            external_id="c-police-divert",
            hours=5.9,
            handle="MumbaiPolice",
            user_id="mumbaipolice",
            text="Traffic diversions on Western Express Highway. Do not use flooded underpasses. @IndiaMetDept",
            polarity="NEUTRAL",
            dominant="realization",
            topic=flood,
            role="comment",
            reply_to=ROOT_IMD,
            severity="high",
            profession="Public sector",
        ),
        _doc(
            platform="x",
            external_id="c-priya-lobby",
            hours=5.7,
            handle="PriyaKamble",
            user_id="priya",
            text="Water entered our building lobby in Wadala. Need pumps. Please send help @ReliefOpsIN",
            polarity="NEGATIVE",
            dominant="fear",
            topic=flood,
            role="comment",
            reply_to=ROOT_IMD,
            severity="high",
            profession="Other",
        ),
        _doc(
            platform="telegram",
            external_id="c-civic-camps",
            hours=5.1,
            handle="CivicWatchMUM",
            user_id="civicwatch",
            text="Confirmed: camps at three schools are taking families. Volunteers at the Dadar gate. @ReliefOpsIN",
            polarity="POSITIVE",
            dominant="approval",
            topic=flood,
            role="comment",
            reply_to=ROOT_RELIEF,
            severity="medium",
            profession="Media",
        ),
        _doc(
            platform="x",
            external_id="c-anand-boat",
            hours=4.8,
            handle="AnandNair",
            user_id="anand",
            text="Volunteer boats on standby near the creek. Roads east of the river still slow. @MumbaiPolice",
            polarity="NEUTRAL",
            dominant="caring",
            topic=flood,
            role="comment",
            reply_to=ROOT_IMD,
            severity="medium",
            profession="Logistics",
        ),
        _doc(
            platform="x",
            external_id="c-meera-anger",
            hours=4.4,
            handle="MeeraDesai",
            user_id="meera",
            text="Drains were not cleared before the alert. This happens every monsoon. @IndiaMetDept",
            polarity="NEGATIVE",
            dominant="anger",
            topic=flood,
            role="comment",
            reply_to=ROOT_IMD,
            severity="medium",
            profession="Engineering",
        ),
        _doc(
            platform="telegram",
            external_id="c-school-thanks",
            hours=4.0,
            handle="DadarSchoolPTA",
            user_id="dadarpta",
            text="Thank you for opening the school as a camp. We have drinking water for 80 people. @ReliefOpsIN",
            polarity="POSITIVE",
            dominant="gratitude",
            topic=flood,
            role="comment",
            reply_to=ROOT_RELIEF,
            severity="low",
            profession="Other",
        ),
        _doc(
            platform="x",
            external_id="c-grid-feeder",
            hours=3.6,
            handle="GridDeskWest",
            user_id="griddesk",
            text="Load shedding shortened in two districts after feeder repair. Crews still in Kurla. @ReliefOpsIN",
            polarity="POSITIVE",
            dominant="relief",
            topic=power,
            role="post",
            severity="medium",
            profession="Engineering",
            hashtags=["power"],
        ),
        _doc(
            platform="x",
            external_id="c-grid-comment",
            hours=3.3,
            handle="LocalPulse",
            user_id="localpulse",
            text="Power is back on our street but the lift is still out. @GridDeskWest",
            polarity="NEUTRAL",
            dominant="disappointment",
            topic=power,
            role="comment",
            reply_to="c-grid-feeder",
            severity="low",
            profession="Other",
            hashtags=["power"],
        ),
        _doc(
            platform="x",
            external_id="c-aqi-north",
            hours=8.0,
            handle="AirIndexIN",
            user_id="airindex",
            text="AQI 312 in the north cluster. Construction pause requested through Friday. @CivicWatchMUM",
            polarity="NEGATIVE",
            dominant="annoyance",
            topic=air,
            role="post",
            severity="medium",
            profession="Research",
            hashtags=["airquality"],
            country="India",
        ),
        _doc(
            platform="telegram",
            external_id="c-aqi-reply",
            hours=7.4,
            handle="NorthDesk",
            user_id="northdesk",
            text="Site managers notified. Dust screens going up tonight. @AirIndexIN",
            polarity="POSITIVE",
            dominant="optimism",
            topic=air,
            role="comment",
            reply_to="c-aqi-north",
            severity="low",
            profession="Engineering",
            hashtags=["airquality"],
        ),
        _doc(
            platform="x",
            external_id="c-port-delay",
            hours=9.2,
            handle="PortNewsIN",
            user_id="portnews",
            text="Berth 4 delay 6h after water on the yard. Perishable cargo rerouted. Not a security incident.",
            polarity="NEUTRAL",
            dominant="neutral",
            topic="port congestion",
            role="post",
            severity="low",
            profession="Logistics",
            hashtags=["logistics"],
        ),
        _doc(
            platform="x",
            external_id="c-volunteer-ration",
            hours=3.0,
            handle="VolunteerIN",
            user_id="volunteerin",
            text="Need dry ration for 40 families near the bus depot. Coordination with the district office. @ReliefOpsIN",
            polarity="NEGATIVE",
            dominant="caring",
            topic=flood,
            role="comment",
            reply_to=ROOT_RELIEF,
            severity="high",
            profession="Other",
        ),
        _doc(
            platform="telegram",
            external_id="c-hydro-gauge",
            hours=2.6,
            handle="HydroAlert",
            user_id="hydroalert",
            text="Hourly gauge: river up 12 cm vs yesterday. Volunteer boats on standby. @IndiaMetDept",
            polarity="NEGATIVE",
            dominant="nervousness",
            topic=flood,
            role="comment",
            reply_to=ROOT_IMD,
            severity="high",
            profession="Research",
        ),
        _doc(
            platform="x",
            external_id="c-transit",
            hours=2.2,
            handle="TransitBot",
            user_id="transitbot",
            text="Suburban line 2 resumed at 40% frequency after water receded from the yard. @MumbaiPolice",
            polarity="POSITIVE",
            dominant="relief",
            topic=flood,
            role="comment",
            reply_to=ROOT_IMD,
            severity="medium",
            profession="Logistics",
        ),
        _doc(
            platform="x",
            external_id="c-us-media",
            hours=4.6,
            handle="WireDesk",
            user_id="wiredesk",
            text="Mumbai monsoon alert drawing civic response. Camps listed by @ReliefOpsIN.",
            polarity="NEUTRAL",
            dominant="curiosity",
            topic=flood,
            role="comment",
            reply_to=ROOT_RELIEF,
            severity="low",
            country="United States",
            language="English",
            profession="Media",
        ),
        _doc(
            platform="telegram",
            external_id="c-uae-family",
            hours=3.8,
            handle="NishaGulf",
            user_id="nisha",
            text="Family in Kurla is at the school camp. Grateful for updates. @ReliefOpsIN",
            polarity="POSITIVE",
            dominant="gratitude",
            topic=flood,
            role="comment",
            reply_to=ROOT_RELIEF,
            severity="low",
            country="UAE",
            language="English",
            profession="Other",
        ),
        _doc(
            platform="x",
            external_id="c-bd-note",
            hours=5.0,
            handle="DhakaWatch",
            user_id="dhakawatch",
            text="Similar waterlogging pattern this week in the east. Watching @IndiaMetDept gauges.",
            polarity="NEUTRAL",
            dominant="realization",
            topic=flood,
            role="comment",
            reply_to=ROOT_IMD,
            severity="low",
            country="Bangladesh",
            language="Bengali",
            profession="Media",
        ),
        _doc(
            platform="x",
            external_id="c-tamil-note",
            hours=2.8,
            handle="ChennaiDesk",
            user_id="chennaidesk",
            text="Reservoir release held overnight. Sharing the Mumbai underpass advisory. @MumbaiPolice",
            polarity="NEUTRAL",
            dominant="caring",
            topic=flood,
            role="comment",
            reply_to=ROOT_IMD,
            severity="low",
            language="Tamil",
            profession="Public sector",
        ),
    ]


_FILLER_HANDLES = [
    ("WardHelp", "wardhelp"),
    ("ResidentRaj", "raj"),
    ("NurseLata", "lata"),
    ("BMCControl", "bmc"),
    ("StudentAsha", "asha"),
    ("DriverVikram", "vikram"),
    ("ShopOwnerKen", "ken"),
    ("CoachRina", "rina"),
]

_FILLER_LINES = [
    "Street still flooded near the market. Waiting on pumps. @{mention}",
    "Families on the first floor moved to the school camp. @{mention}",
    "Need drinking water packets at the bus depot. @{mention}",
    "Kids are safe. Looking for dry clothes. @{mention}",
    "Road closed at the underpass. Turned back. @{mention}",
    "Power flickered twice. Phones almost dead. @{mention}",
    "Shared the camp address with neighbours. @{mention}",
    "River edge is higher than this morning. @{mention}",
]


def _fillers(*, start_hours: float, count: int, prefix: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    mentions = ("IndiaMetDept", "ReliefOpsIN", "MumbaiPolice")
    polarities = [
        ("NEGATIVE", "fear"),
        ("NEGATIVE", "sadness"),
        ("POSITIVE", "approval"),
        ("NEGATIVE", "annoyance"),
        ("NEUTRAL", "neutral"),
        ("POSITIVE", "caring"),
        ("NEGATIVE", "nervousness"),
        ("POSITIVE", "gratitude"),
    ]
    for index in range(count):
        handle, user_id = _FILLER_HANDLES[index % len(_FILLER_HANDLES)]
        line = _FILLER_LINES[index % len(_FILLER_LINES)]
        mention = mentions[index % len(mentions)]
        polarity, dominant = polarities[index % len(polarities)]
        # Cluster into the target hour so velocity uses a stable sample size.
        hour_offset = start_hours - (index % 50) * 0.01
        rows.append(
            _doc(
                platform="x" if index % 2 == 0 else "telegram",
                external_id=f"{prefix}-{index}",
                hours=hour_offset,
                handle=handle,
                user_id=user_id,
                text=line.format(mention=mention),
                polarity=polarity,
                dominant=dominant,
                topic="flood relief",
                role="comment",
                reply_to=ROOT_IMD if index % 2 == 0 else ROOT_RELIEF,
                severity="medium" if index % 3 else "high",
                profession="Other",
                score=0.52 + (index % 7) * 0.02,
            )
        )
    return rows


def _ticker_comments() -> list[dict[str, Any]]:
    return [
        _doc(
            platform="x",
            external_id="live-1",
            hours=0.02,
            handle="PriyaKamble",
            user_id="priya",
            text="Update: municipal pump arrived at Wadala lobby. Water dropping. @ReliefOpsIN",
            polarity="POSITIVE",
            dominant="relief",
            topic="flood relief",
            role="comment",
            reply_to=ROOT_IMD,
            severity="medium",
        ),
        _doc(
            platform="telegram",
            external_id="live-2",
            hours=0.02,
            handle="CivicWatchMUM",
            user_id="civicwatch",
            text="Kurla camp now at 55 people. Still accepting families. @ReliefOpsIN",
            polarity="NEUTRAL",
            dominant="realization",
            topic="flood relief",
            role="comment",
            reply_to=ROOT_RELIEF,
            severity="medium",
        ),
        _doc(
            platform="x",
            external_id="live-3",
            hours=0.02,
            handle="MeeraDesai",
            user_id="meera",
            text="WEH diversion is working. Still angry about the drains. @MumbaiPolice",
            polarity="NEGATIVE",
            dominant="annoyance",
            topic="flood relief",
            role="comment",
            reply_to=ROOT_IMD,
            severity="low",
        ),
        _doc(
            platform="x",
            external_id="live-4",
            hours=0.02,
            handle="VolunteerIN",
            user_id="volunteerin",
            text="Ration kits delivered to 22 of 40 families. Need two more vans. @ReliefOpsIN",
            polarity="POSITIVE",
            dominant="approval",
            topic="flood relief",
            role="comment",
            reply_to=ROOT_RELIEF,
            severity="medium",
        ),
        _doc(
            platform="telegram",
            external_id="live-5",
            hours=0.02,
            handle="HydroAlert",
            user_id="hydroalert",
            text="Gauge steady for 20 minutes. Not falling yet. @IndiaMetDept",
            polarity="NEGATIVE",
            dominant="fear",
            topic="flood relief",
            role="comment",
            reply_to=ROOT_IMD,
            severity="high",
        ),
        _doc(
            platform="x",
            external_id="live-6",
            hours=0.02,
            handle="GridDeskWest",
            user_id="griddesk",
            text="Kurla feeder back to 80%. Lift outages should clear. @LocalPulse",
            polarity="POSITIVE",
            dominant="optimism",
            topic="power outage",
            role="comment",
            reply_to="c-grid-feeder",
            severity="low",
            hashtags=["power"],
        ),
        _doc(
            platform="x",
            external_id="live-7",
            hours=0.02,
            handle="TransitBot",
            user_id="transitbot",
            text="Line 2 now at 60% frequency. Avoid the creek-side entrance. @MumbaiPolice",
            polarity="POSITIVE",
            dominant="relief",
            topic="flood relief",
            role="comment",
            reply_to=ROOT_IMD,
            severity="medium",
        ),
        _doc(
            platform="telegram",
            external_id="live-8",
            hours=0.02,
            handle="DadarSchoolPTA",
            user_id="dadarpta",
            text="Hot meal line started. 80 portions. @ReliefOpsIN",
            polarity="POSITIVE",
            dominant="gratitude",
            topic="flood relief",
            role="comment",
            reply_to=ROOT_RELIEF,
            severity="low",
        ),
    ]


def initial_documents() -> list[dict[str, Any]]:
    """Posts persisted at startup (enough for a trend spike on flood relief)."""
    # Previous hour ~20, current hour ~52 → velocity 2.6 and sample_size > 50.
    return (
        _unique_thread()
        + _fillers(start_hours=1.6, count=20, prefix="prev")
        + _fillers(start_hours=0.55, count=52, prefix="now")
    )


def ticker_documents() -> list[dict[str, Any]]:
    return _ticker_comments()


def reset_demo_seed_state() -> None:
    global _loaded
    _ticker.clear()
    _loaded = False


def pop_ticker_document() -> dict[str, Any] | None:
    if not _ticker:
        return None
    return _ticker.popleft()


def load_demo_seed(*, persist) -> int:
    """Idempotent load into the current process stores via persist(document)."""
    global _loaded
    if _loaded:
        return 0
    count = 0
    for document in initial_documents():
        persist(document)
        count += 1
    _ticker.clear()
    _ticker.extend(ticker_documents())
    _loaded = True
    logger.info("Demo seed loaded (%s posts/comments)", count)
    return count
