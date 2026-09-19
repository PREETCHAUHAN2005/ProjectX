"""Local demo raw posts shaped like Telegram / X events.

IMPLEMENTATION (CHG-018-style resilience). Used when live X/Telegram
credentials or scrapers are unavailable. Posts still go through normalize
→ inference → stores → REST/WS. Not a confirmed product dataset.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from workers.ingestion.raw_post import utc_now_iso

_CYBER = (
    "Phishing kit targeting {place} bank customers. @{mention} please amplify to volunteers.",
    "Malware campaign using fake {place} electricity bills. Analysts tracing C2 nodes.",
    "Credential stuffing against a civic portal in {place}. Reset advisory going out.",
    "Ransomware note hit a logistics vendor near {place}. Night-shift engineer on call.",
    "Fake cyber-cell donation page circulating. Analysts in {place} issued a takedown request.",
    "SMS malware lures mention civic portals in {place}. Do not tap the short link.",
)

_FLOOD = (
    "Relief kits staged at three municipal schools in {place}. Roads east of the river still slow. @{mention}",
    "Hourly gauge: river up 12 cm vs yesterday near {place}. Volunteer boats on standby.",
    "Need dry ration for 40 families near the bus depot in {place}. Coordinating with the district office.",
    "NDRF team reached {place} after overnight flood. @{mention} coordinating boats.",
    "Public advisory: avoid low-lying underpasses in {place} until 18:00 IST. Pumps are active.",
    "Suburban line resumed at 40% frequency after water receded from the yard in {place}.",
)

_ELECTION = (
    "Polling booth accessibility check in {place}. Queue moving. @{mention} on site.",
    "Campaign convoy delayed on the highway into {place}. Traffic police diversion in effect.",
    "Voter helpline volume spiking in {place}. Officials asked journalists not to crowd the gate.",
    "EVM sealing photos from {place} shared by the returning officer. No incident reported.",
)

_BORDER = (
    "Fog reduced visibility on the patrol track near {place}. Extra watch till dawn.",
    "Forward post rotation completed near {place}. No firing reported in the last window.",
    "Civilian traffic paused on the border road to {place} for a short engineering party.",
)

_POWER = (
    "Load shedding window shortened in two districts around {place} after feeder repair.",
    "Grid desk: transformer trip at {place} cleared. Engineers restoring the last feeder.",
    "Overnight outage in {place} markets. Municipal pumps still on generator.",
)

_HEALTH = (
    "AQI 312 in the north cluster of {place}. Construction pause requested through Friday.",
    "Hospital surge beds in {place} remain available. Health official briefing at 16:00.",
    "Vaccination camp at the district school in {place}. Volunteers requested after 11:00.",
)

_PLACES = (
    "Guwahati",
    "Patna",
    "Chennai",
    "Mumbai",
    "Delhi",
    "Kolkata",
    "Srinagar",
    "Kochi",
    "Bengaluru",
    "Ladakh",
)
_MENTIONS = ("ndrf", "citywatch", "griddesk", "cybercell", "reliefops", "electioncomm", "borderwatch")
_HANDLES = (
    ("x", "reliefops"),
    ("telegram", "citywatch"),
    ("x", "griddesk"),
    ("telegram", "floodcell"),
    ("x", "airindex"),
    ("x", "cyberdesk"),
    ("telegram", "portnews"),
    ("x", "volunteerin"),
    ("telegram", "districtcell"),
    ("x", "transitbot"),
)


def _stamp(hours_ago: float, minute: int = 8) -> str:
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    point = now - timedelta(hours=hours_ago, minutes=max(0, 12 - minute))
    return point.isoformat()


def _item(
    *,
    index: int,
    platform: str,
    handle: str,
    text: str,
    hours_ago: float,
    language: str,
    extra_id: str,
) -> dict[str, Any]:
    hashtags = []
    lowered = text.lower()
    if "flood" in lowered or "inundat" in lowered:
        hashtags.append("floodrelief")
    if "malware" in lowered or "phishing" in lowered or "ransomware" in lowered:
        hashtags.append("cyber")
    if "poll" in lowered or "voter" in lowered or "evm" in lowered:
        hashtags.append("elections")
    return {
        "platform": platform,
        "external_id": extra_id,
        "timestamp": _stamp(hours_ago, minute=index % 50),
        "author": {
            "user_id": f"u-{handle}",
            "handle": handle,
            "bio": f"Public updates from {handle}",
            "follower_count": 800 + (index * 37) % 12000,
        },
        "content": {
            "raw_text": text,
            "hashtags": hashtags or None,
            "language": language,
        },
        "engagement": {
            "likes": (index * 11) % 400,
            "shares": (index * 3) % 80,
            "views": 200 + (index * 17) % 8000,
        },
        "ingested_at": utc_now_iso(),
    }


def _fill(templates: tuple[str, ...], n: int, hours_ago: float, start: int, prefix: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(n):
        template = templates[i % len(templates)]
        place = _PLACES[i % len(_PLACES)]
        mention = _MENTIONS[i % len(_MENTIONS)]
        platform, handle = _HANDLES[(start + i) % len(_HANDLES)]
        language = "Hindi" if i % 7 == 0 else "English"
        text = template.format(place=place, mention=mention)
        if i % 5 == 0:
            text = f"{text} Journalist pool on site."
        elif i % 5 == 1:
            text = f"{text} Volunteer desk asked for an engineer."
        rows.append(
            _item(
                index=start + i,
                platform=platform,
                handle=handle,
                text=text,
                hours_ago=hours_ago + (i % 4) * 0.05,
                language=language,
                extra_id=f"{prefix}-{i}",
            )
        )
    return rows


def seed_raw_posts() -> list[dict[str, Any]]:
    """Historical window plus a cyber burst that can trip the spike rule."""
    rows: list[dict[str, Any]] = []
    rows.extend(_fill(_CYBER, 62, 0.05, 0, "cyber-now"))
    rows.extend(_fill(_CYBER, 18, 1.0, 62, "cyber-prev"))
    rows.extend(_fill(_FLOOD, 22, 2.0, 80, "flood"))
    rows.extend(_fill(_ELECTION, 14, 4.0, 110, "elect"))
    rows.extend(_fill(_BORDER, 10, 6.0, 130, "border"))
    rows.extend(_fill(_POWER, 10, 8.0, 150, "power"))
    rows.extend(_fill(_HEALTH, 8, 10.0, 170, "health"))
    for hour in range(12, 24):
        rows.extend(_fill(_FLOOD, 1, float(hour), 200 + hour, f"hist-{hour}"))
    return rows


def live_raw_post(tick: int) -> dict[str, Any]:
    """One incoming post for the realtime loop (timestamp = now)."""
    pools = (_FLOOD, _CYBER, _ELECTION, _POWER, _BORDER, _HEALTH)
    templates = pools[tick % len(pools)]
    template = templates[tick % len(templates)]
    place = _PLACES[tick % len(_PLACES)]
    mention = _MENTIONS[tick % len(_MENTIONS)]
    platform, handle = _HANDLES[tick % len(_HANDLES)]
    text = template.format(place=place, mention=mention)
    post = _item(
        index=tick,
        platform=platform,
        handle=handle,
        text=text,
        hours_ago=0,
        language="English" if tick % 4 else "Hindi",
        extra_id=f"live-{tick}-{utc_now_iso()}",
    )
    post["timestamp"] = utc_now_iso()
    return post
