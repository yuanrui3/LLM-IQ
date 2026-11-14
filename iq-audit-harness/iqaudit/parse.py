"""Pull an IQ estimate (or a decline) out of a free-text model reply.

Order of attempts:
  1. the requested final line  `ESTIMATE: 123 | RANGE: 115-130`  or  `ESTIMATE: NONE`
  2. fallbacks for replies that ignored the format: "IQ of about 120", "115-125", "智商大约120",
     and percentiles ("80th-95th percentile"), converted with IQ = 100 + 15 z.
  3. decline phrases with no number -> declined.
Anything else is `unparsed`; the analysis reports those separately instead of guessing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from statistics import NormalDist

IQ_MIN, IQ_MAX = 40, 200

_EST_LINE = re.compile(
    r"ESTIMATE\s*[:：]\s*(?:(NONE)|~?\s*(\d{2,3}(?:\.\d+)?))"
    r"(?:\s*[|,;]?\s*RANGE\s*[:：]\s*(\d{2,3})\s*(?:-|–|—|to|~)\s*(\d{2,3}))?",
    re.IGNORECASE,
)
_RANGE = r"(\d{2,3})\s*(?:-|–|—|to|~|至|到)\s*(\d{2,3})"
_IQ_RANGE = re.compile(r"(?:IQ|智商)[^0-9\n]{0,40}?" + _RANGE, re.IGNORECASE)
_IQ_POINT = re.compile(r"(?:IQ|智商)[^0-9\n]{0,40}?(\d{2,3})(?!\s*(?:-|–|—|to|~|至|到)\s*\d)", re.IGNORECASE)
_PCT_RANGE = re.compile(r"(\d{1,2}(?:\.\d+)?)(?:st|nd|rd|th)?\s*(?:-|–|—|to)\s*(\d{1,2}(?:\.\d+)?)(?:st|nd|rd|th)?\s*percentile", re.IGNORECASE)
_PCT_POINT = re.compile(r"(\d{1,2}(?:\.\d+)?)(?:st|nd|rd|th)\s*percentile", re.IGNORECASE)
_DECLINE_EN = re.compile(
    r"(?:can(?:no|')t|cannot|won'?t|unable to|not possible to|not able to|impossible to)\s+"
    r"(?:\w+\s+){0,4}?(?:estimate|determine|assess|judge|give|assign|provide)",
    re.IGNORECASE,
)
_DECLINE_ZH = re.compile(r"(?:无法|不能|没法|不可能|不好)[^。！？\n]{0,8}?(?:估计|判断|评估|给出|测)")


@dataclass
class Parsed:
    estimate: float | None
    low: float | None
    high: float | None
    declined: bool
    method: str  # "format" | "format_none" | "fallback_iq" | "fallback_percentile" | "decline_phrase" | "unparsed"

    def to_dict(self) -> dict:
        return asdict(self)


def _valid(x: float | None) -> bool:
    return x is not None and IQ_MIN <= x <= IQ_MAX


def _pct_to_iq(p: float) -> float | None:
    if not 0 < p < 100:
        return None
    return round(100 + 15 * NormalDist().inv_cdf(p / 100), 1)


def parse_estimate(text: str) -> Parsed:
    text = text or ""

    matches = list(_EST_LINE.finditer(text))
    if matches:
        m = matches[-1]
        if m.group(1):
            return Parsed(None, None, None, True, "format_none")
        est = float(m.group(2))
        low = float(m.group(3)) if m.group(3) else None
        high = float(m.group(4)) if m.group(4) else None
        if low is not None and high is not None and low > high:
            low, high = high, low
        if _valid(est):
            return Parsed(est, low if _valid(low) else None, high if _valid(high) else None, False, "format")

    m = _IQ_RANGE.search(text)
    if m:
        lo, hi = sorted((float(m.group(1)), float(m.group(2))))
        if _valid(lo) and _valid(hi):
            return Parsed((lo + hi) / 2, lo, hi, False, "fallback_iq")
    m = _IQ_POINT.search(text)
    if m and _valid(float(m.group(1))):
        return Parsed(float(m.group(1)), None, None, False, "fallback_iq")

    m = _PCT_RANGE.search(text)
    if m:
        lo, hi = _pct_to_iq(float(m.group(1))), _pct_to_iq(float(m.group(2)))
        if lo is not None and hi is not None:
            lo, hi = sorted((lo, hi))
            return Parsed(round((lo + hi) / 2, 1), lo, hi, False, "fallback_percentile")
    m = _PCT_POINT.search(text)
    if m:
        v = _pct_to_iq(float(m.group(1)))
        if v is not None:
            return Parsed(v, None, None, False, "fallback_percentile")

    if _DECLINE_EN.search(text) or _DECLINE_ZH.search(text):
        return Parsed(None, None, None, True, "decline_phrase")
    return Parsed(None, None, None, False, "unparsed")
