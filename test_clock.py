"""Tests for clock.py. Standard library only: python -m unittest"""
import random, unittest
from datetime import datetime
from clock import LEVELS, RANK, reach, level, due, target, clock_errors, add_business_days

WED = datetime(2026, 9, 23, 9, 30); FRI = datetime(2026, 9, 25, 9, 30); SAT = datetime(2026, 9, 26, 9, 30)
def p(high, medium, low): return {"high": high, "medium": medium, "low": low}
def jev(dist, safety=0.01, reply=0.99): return {"urgency": {"p": dist}, "flags": {"safety": safety, "needs_reply": reply}}
def row(i, dist, ref, safety=0.01, reply=0.99): return {"id": i, "jev": jev(dist, safety, reply), "seed": {"urgency": ref}}

class Level(unittest.TestCase):
    def test_median_uses_the_ordering_argmax_ignores(self):
        # M22 in the demo run: argmax is "low", but medium-or-worse is 0.61
        self.assertEqual(level(p(0.25, 0.36, 0.39)), "medium")

    def test_clear_cases_match_argmax(self):
        self.assertEqual(level(p(1.0, 0.0, 0.0)), "high")
        self.assertEqual(level(p(0.02, 0.98, 0.0)), "medium")
        self.assertEqual(level(p(0.0, 0.0, 1.0)), "low")

    def test_lower_threshold_is_more_cautious(self):
        dist = p(0.33, 0.67, 0.0)
        self.assertEqual(level(dist, 0.5), "medium")
        self.assertEqual(level(dist, 0.3), "high")

    def test_threshold_is_inclusive(self):
        self.assertEqual(level(p(0.5, 0.5, 0.0), 0.5), "high")

    def test_probabilities_rounding_short_of_one_still_get_a_clock(self):
        self.assertEqual(level(p(0.0, 0.0, 0.999), 1.0), "low")

    def test_a_plurality_high_below_the_median_keeps_the_high_clock(self):
        # the median alone is "medium" here, which would put a 1-day clock next to an "Acuity: High" label
        self.assertEqual(reach(p(0.4, 0.35, 0.25)), "medium")
        self.assertEqual(level(p(0.4, 0.35, 0.25)), "high")

    def test_the_floor_is_jevs_own_choice_when_given(self):
        # on an exact tie argmax of the dict depends on key order; the label the viewer shows is Jev's choice
        self.assertEqual(level(p(0.1, 0.45, 0.45), 0.5, shown="medium"), "medium")
        self.assertEqual(level(p(0.1, 0.45, 0.45), 0.5, shown="low"), "medium")    # the median still tightens

    def test_never_looser_than_the_displayed_label(self):
        rng = random.Random(0)
        for _ in range(5000):
            w = [rng.random() ** 3 for _ in LEVELS]; dist = dict(zip(LEVELS, (x / sum(w) for x in w)))
            argmax = max(dist, key=dist.get)
            for t in (0.05, 0.3, 0.5, 0.7, 0.95):
                self.assertGreaterEqual(RANK[level(dist, t)], RANK[argmax], (dist, t))

class Due(unittest.TestCase):
    def test_high_is_wall_clock_hours(self):
        self.assertEqual(due(WED, "high"), datetime(2026, 9, 23, 13, 30))

    def test_medium_is_same_time_next_business_day(self):
        self.assertEqual(due(WED, "medium"), datetime(2026, 9, 24, 9, 30))

    def test_friday_rolls_over_the_weekend(self):
        self.assertEqual(due(FRI, "medium"), datetime(2026, 9, 28, 9, 30))   # Monday

    def test_low_is_three_business_days(self):
        self.assertEqual(due(WED, "low"), datetime(2026, 9, 28, 9, 30))      # Thu, Fri, Mon

    def test_weekend_arrival_counts_from_monday(self):
        self.assertEqual(add_business_days(SAT, 1), datetime(2026, 9, 28, 9, 30))

class Target(unittest.TestCase):
    def test_safety_goes_to_call_now_with_no_portal_clock(self):
        self.assertEqual(target(jev(p(0.0, 0.0, 1.0), safety=0.98), WED), (None, None))

    def test_no_reply_needed_gets_no_clock(self):
        self.assertEqual(target(jev(p(0.0, 0.0, 1.0), reply=0.02), WED), (None, None))

    def test_otherwise_level_and_due(self):
        self.assertEqual(target(jev(p(0.25, 0.36, 0.39)), WED), ("medium", datetime(2026, 9, 24, 9, 30)))

class Errors(unittest.TestCase):
    ROWS = [row("A", p(0.25, 0.36, 0.39), "medium"),    # argmax too loose, median right
            row("B", p(0.0, 0.99, 0.01), "low"),        # too tight either way
            row("C", p(1.0, 0.0, 0.0), "high", safety=0.98),
            row("D", p(0.0, 0.0, 1.0), "low", reply=0.02)]

    def test_counts_loose_tight_and_unclocked(self):
        self.assertEqual(clock_errors(self.ROWS), ([], ["B"], ["C", "D"]))

    def test_argmax_comparison(self):
        argmax = lambda r: max(r["jev"]["urgency"]["p"], key=r["jev"]["urgency"]["p"].get)
        self.assertEqual(clock_errors(self.ROWS, pick=argmax), (["A"], ["B"], ["C", "D"]))

if __name__ == "__main__":
    unittest.main()
