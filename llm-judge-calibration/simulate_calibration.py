"""Show position-bias mitigation flipping a biased win into a TIE, then
report judge/human agreement via Cohen's kappa.

    $ python3 simulate_calibration.py
"""

from __future__ import annotations

from judge import judge_pair, _raw_verdict, cohens_kappa

Q = "how do I reset my password"
# Two near-equal answers; a naive judge would pick whichever is shown first.
A = "Go to settings and reset your password."
B = "Open settings, then reset your password."


def main() -> None:
    naive_AB = _raw_verdict(Q, A, B)   # A shown first
    naive_BA = _raw_verdict(Q, B, A)   # B shown first
    print(f"naive judge, A first: prefers {naive_AB}")
    print(f"naive judge, B first: prefers {naive_BA}")
    print(f"bias-mitigated verdict: {judge_pair(Q, A, B)}")
    assert judge_pair(Q, A, B) == "TIE", "swap-consistent -> TIE on a real tie"

    # A clearly better answer still wins after mitigation.
    weak = "Your password is important."
    assert judge_pair(Q, A, weak) == "A"
    print(f"\nclear winner survives mitigation: {judge_pair(Q, A, weak)}")

    # Calibration vs a human panel.
    judge_labels = ["A", "B", "TIE", "A", "A", "B"]
    human_labels = ["A", "B", "TIE", "A", "TIE", "B"]
    k = cohens_kappa(judge_labels, human_labels)
    print(f"\njudge/human Cohen's kappa: {k:.2f}")
    assert k > 0.5
    print("OK: position bias corrected; agreement measured before trusting the gate.")


if __name__ == "__main__":
    main()
