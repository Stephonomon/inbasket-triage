"""Response-time targets started from Jev's urgency probabilities (policy layer: code, not model).

  level    The more urgent of two readings. (1) The most urgent level the message is at least CLOCK_T likely to reach:
           walk high -> medium -> low adding probability until the running total clears CLOCK_T; at 0.5 this is the
           median of the ordinal distribution. (2) The acuity label the viewer already shows (argmax).
           Argmax alone ignores the ordering: 0.39 low / 0.36 medium / 0.25 high picks "low" although medium-or-worse
           is 0.61. The median alone can loosen a clock: 0.40 high / 0.35 medium / 0.25 low has a median of "medium"
           next to an "Acuity: High" label. Taking the more urgent of the two can tighten a clock, never loosen one.
           Lower CLOCK_T is more cautious: at 0.3 a 30% chance of "high" starts the high clock.
  due      Received time plus the level's window. Hours are wall-clock; business days skip Saturday and Sunday
           (no holiday calendar). Messages that go to Call Now, and FYI messages that need no reply, get no clock.

The windows come from the urgency definitions in data.py (high: within hours, today; medium: 1 business day;
low: 2-3 business days). Averaging the windows by probability is deliberately not offered: it would turn a 25% chance
of an emergency into a middling deadline.
"""
from datetime import timedelta

LEVELS = ("high", "medium", "low")                     # most urgent first
WINDOWS = {"high": ("hours", 4), "medium": ("business_days", 1), "low": ("business_days", 3)}
CLOCK_T = 0.5; SAFETY_T = 0.5; REPLY_T = 0.5         # SAFETY_T and REPLY_T match FLAG_T in triage.py

RANK = {"low": 0, "medium": 1, "high": 2}
def reach(p, t=CLOCK_T):
    run = 0.0
    for k in LEVELS:
        run += p.get(k, 0.0)
        if run >= t - 1e-9: return k
    return LEVELS[-1]                                    # probabilities that round to just under 1

def level(p, t=CLOCK_T, shown=None):
    """`shown` is the acuity label the viewer displays (Jev's choice); argmax of `p` when not given."""
    return max(reach(p, t), shown or max(p, key=p.get), key=RANK.get)

def add_business_days(when, n):
    while n > 0:
        when += timedelta(days=1)
        if when.weekday() < 5: n -= 1
    return when

def due(received, lvl, windows=WINDOWS):
    unit, n = windows[lvl]
    return received + timedelta(hours=n) if unit == "hours" else add_business_days(received, n)

def clocked(j, safety_t=SAFETY_T):
    return j["flags"]["safety"] < safety_t and j["flags"]["needs_reply"] >= REPLY_T

def target(j, received, t=CLOCK_T, safety_t=SAFETY_T):
    """(level, due) for one message's Jev answers, or (None, None) when it gets no clock: Call Now, or no reply needed."""
    if not clocked(j, safety_t): return None, None
    lvl = level(j["urgency"]["p"], t, j["urgency"].get("choice"))
    return lvl, due(received, lvl)

def clock_errors(rows, t=CLOCK_T, safety_t=SAFETY_T, pick=None):
    """Compare each message's clock level with its reference urgency. Returns (too_loose, too_tight, no_clock) id lists.
    `pick(r)` overrides the level rule, e.g. argmax, for comparison. Messages with no clock are listed separately."""
    loose, tight, none = [], [], []
    for r in rows:
        if not clocked(r["jev"], safety_t): none.append(r["id"]); continue
        u = r["jev"]["urgency"]; got = pick(r) if pick else level(u["p"], t, u.get("choice")); ref = r["seed"]["urgency"]
        if RANK[got] < RANK[ref]: loose.append(r["id"])
        elif RANK[got] > RANK[ref]: tight.append(r["id"])
    return loose, tight, none
