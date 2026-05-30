# SteadyStateQualityDrift

**HEADLINE:** Weekly quality score dropped below the rolling baseline.

**FIRST CHECK:** Open the steady-state drift panel. Is the drop sustained over
two weeks, or a single noisy week? Single week → note and watch, do not act.

**SECOND CHECK:** Check whether the eval prompt set changed or production traffic
mix shifted. A traffic shift is expected drift, not a regression.

**ROLLBACK GATE:** If the two-week drop exceeds 3 points and z-score is above 1.5,
revert to the last release whose baseline the current scores still clear.

**ESCALATE:** Open a postmortem if the drift is confirmed as a regression and the
revert does not restore the baseline within one eval cycle.
