#!/usr/bin/env python3
"""Recommend a 6 GHz power mode (LPI or Standard Power) for a site.

Asks yes/no questions about the deployment and prints a recommendation
with the reasons behind it. Stdlib only. Run interactively:

    python3 decide.py

or non-interactively with answers in question order (y/n):

    python3 decide.py --answers y,n,n,y,y,n,n

Print the comparison table instead:

    python3 decide.py --table
"""
import argparse
import csv
import os
import sys

# (question, mode-it-pushes-toward, weight, reason-shown-when-yes)
QUESTIONS = [
    ("Is this a one-for-one AP replacement on existing cable drops "
     "(no new cabling, no placement redesign)?",
     "sp", 2,
     "One-for-one swaps under LPI produce coverage holes between drops "
     "because of the 6 dB client penalty. Standard Power closes that gap."),
    ("Do you have coverage complaints where clients see the AP fine but "
     "uploads and roams fail at the cell edge?",
     "sp", 2,
     "That is the client talk-back failure pattern. Standard Power removes "
     "the client power restriction."),
    ("Are 80 or 160 MHz channels a requirement (large file transfer, "
     "special-purpose clients)?",
     "lpi", 3,
     "AFC exclusion masks break wide contiguous channel blocks. Wide "
     "channels belong in LPI, where PSD rules preserve SNR."),
    ("Are most client devices phones and tablets with routine traffic "
     "(streaming, browsing, messaging)?",
     "sp", 1,
     "Mobile-first clients need a few megabits each. A 40 MHz Standard "
     "Power plan serves them and keeps enough channels despite the masks."),
    ("Can your APs get reliable geolocation (GNSS anchors near windows, "
     "few derivation hops, known heights)?",
     "sp", 2,
     "AFC grants depend on location accuracy. Good geolocation makes "
     "Standard Power practical."),
    ("Is the team unwilling to run AFC operations (cloud onboarding, "
     "location provisioning, monitoring 24-hour re-authorizations)?",
     "lpi", 3,
     "Standard Power adds a standing operational dependency on an "
     "external database. Unstaffed, that dependency becomes outages."),
    ("Is this a high-density space where clients sit close to the APs "
     "(classrooms, dense office, indoor stadium seating)?",
     "lpi", 1,
     "Short client distances do not need the extra talk-back power, and "
     "LPI keeps the maximum channel count for reuse."),
]

CAVEATS = [
    "A Standard Power AP that fails its AFC check-in falls back to LPI on "
    "its own, so the LPI coverage picture is your worst case either way.",
    "Survey for client talk-back, not just AP signal.",
    "40 MHz is a sound default channel width in either mode.",
    "Regulatory rules vary by country. Confirm current rules for your "
    "regulatory domain before deploying.",
]


def ask(question):
    while True:
        answer = input(f"{question} [y/n] ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please answer y or n.")


def print_table():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "modes.csv")
    with open(path, newline="") as handle:
        rows = list(csv.reader(handle))
    widths = [max(len(row[i]) for row in rows) for i in range(3)]
    for index, row in enumerate(rows):
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
        if index == 0:
            print("  ".join("-" * widths[i] for i in range(3)))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--answers",
                        help="comma-separated y/n answers in question order")
    parser.add_argument("--table", action="store_true",
                        help="print the LPI vs Standard Power comparison")
    args = parser.parse_args()

    if args.table:
        print_table()
        return 0

    if args.answers:
        raw = [a.strip().lower() for a in args.answers.split(",")]
        if len(raw) != len(QUESTIONS) or not set(raw) <= {"y", "n"}:
            parser.error(f"--answers needs {len(QUESTIONS)} comma-separated "
                         "y/n values")
        answers = [a == "y" for a in raw]
    else:
        print("Answer for the site you are designing, not the ideal site.\n")
        answers = [ask(question) for question, _, _, _ in QUESTIONS]

    scores = {"lpi": 0, "sp": 0}
    reasons = {"lpi": [], "sp": []}
    for answered_yes, (_, mode, weight, reason) in zip(answers, QUESTIONS):
        if answered_yes:
            scores[mode] += weight
            reasons[mode].append(reason)

    print()
    if scores["sp"] > scores["lpi"]:
        pick, other = "sp", "lpi"
        print("Recommendation: Standard Power "
              f"(score {scores['sp']} to {scores['lpi']}).")
    elif scores["lpi"] > scores["sp"]:
        pick, other = "lpi", "sp"
        print("Recommendation: Low Power Indoor "
              f"(score {scores['lpi']} to {scores['sp']}).")
    else:
        pick, other = None, None
        print(f"No clear lean (score {scores['lpi']} to {scores['sp']}). "
              "Default to LPI: it has no operational dependency, and you "
              "can enable Standard Power later if talk-back coverage "
              "demands it.")

    if pick:
        print("\nWhy:")
        for reason in reasons[pick]:
            print(f"  * {reason}")
        if reasons[other]:
            print("\nPulling the other way:")
            for reason in reasons[other]:
                print(f"  * {reason}")

    print("\nRegardless of mode:")
    for caveat in CAVEATS:
        print(f"  * {caveat}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
