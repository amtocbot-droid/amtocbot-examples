# PostDeployToolErrorSpike

**HEADLINE:** Tool error rate spiked right after a release. Likely the new build.

**FIRST CHECK:** Open the post-deploy dashboard. Is the spike scoped to one
tool, or fleet-wide? One tool → tool regression. Fleet-wide → provider incident.

**SECOND CHECK:** Compare the candidate release tag against the previous one in
the cohort panel. If error rate for the new tag is >2x the old tag, it is the build.

**ROLLBACK GATE:** If the new-tag tool error rate is above 5% for 10 consecutive
minutes, roll back to the previous release tag now. Do not wait for a root cause.

**ESCALATE:** Page the owning team if rollback does not drop error rate below 2%
within 15 minutes, or if the spike is fleet-wide (provider incident).
