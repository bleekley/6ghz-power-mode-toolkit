#!/usr/bin/env python3
"""Recommend a 6 GHz power mode (LPI or Standard Power) for a site.

Asks yes/no questions about the deployment and prints a recommendation
with the reasons behind it. The first three questions are prerequisites:
Standard Power is never recommended while any of them fails, no matter
how the preference questions land.

Scope: indoor deployments where LPI is available as the fallback mode.
Outdoor and Standard-Power-only designs are out of scope; LPI is an
indoor-only mode and cannot be the answer there. Stdlib only. Run
interactively:

    python3 decide.py

or non-interactively with answers in question order (y/n):

    python3 decide.py --answers y,y,y,n,n,y,y,n

Print the comparison table instead:

    python3 decide.py --table
"""
import argparse
import csv
import os
import sys

# Prerequisites. A "no" on any of these blocks a Standard Power
# recommendation outright: (question, what-is-missing-when-no)
GATES = [
    ("Are your APs and clients Standard Power capable, in a regulatory "
     "domain where Standard Power with AFC is authorized?",
     "Standard Power capable hardware in an authorized regulatory domain"),
    ("Can your APs get reliable geolocation (GNSS anchors near windows, "
     "few derivation hops, known heights)?",
     "reliable AP geolocation, which every AFC grant depends on"),
    ("Is the team willing to own AFC operations (cloud onboarding, "
     "location provisioning, monitoring 24-hour re-authorizations)?",
     "an owner for the standing AFC operational dependency"),
]

# Preferences, scored only when every gate passes:
# (question, mode-it-pushes-toward, weight, reason-shown-when-yes)
QUESTIONS = [
    ("Is this a one-for-one AP replacement on existing cable drops "
     "(no new cabling, no placement redesign)?",
     "sp", 2,
     "One-for-one swaps under LPI often leave coverage holes between "
     "drops, because LPI caps both AP and client power lower. Standard "
     "Power raises both ceilings and can narrow that gap; verify with "
     "a survey."),
    ("Do you have coverage complaints where clients see the AP fine but "
     "uploads and roams fail at the cell edge?",
     "sp", 2,
     "That is the client talk-back failure pattern. Standard Power "
     "raises the client power ceiling, which helps exactly this. The "
     "client stays capped at least 6 dB below the AP's authorized "
     "power."),
    ("Are 80 or 160 MHz channels a requirement (large file transfer, "
     "special-purpose clients)?",
     "lpi", 2,
     "AFC exclusions can break wide contiguous blocks, depending on the "
     "grant at your location. Wide-channel plans are safer in LPI, "
     "where the PSD rules scale power with width."),
    ("Are most client devices phones and tablets with routine traffic "
     "(streaming, browsing, messaging)?",
     "sp", 1,
     "Mobile-first clients need a few megabits each. A 40 MHz plan "
     "serves them in either mode, which keeps a Standard Power channel "
     "plan workable despite mask losses."),
    ("Is this a high-density space where clients sit close to the APs "
     "(classrooms, dense office, indoor stadium seating)?",
     "lpi", 1,
     "Short client distances do not need the extra talk-back power, and "
     "LPI keeps the maximum channel count for reuse."),
]

CAVEATS = [
    "This tool assumes an indoor site where LPI is available. Outdoor "
    "and Standard-Power-only designs need a different analysis.",
    "Standard Power does not make the link symmetric: clients are "
    "capped at least 6 dB below the AP's authorized power. It raises "
    "the ceilings for both sides.",
    "Fallback on AFC failure varies by product. The rules allow a grace "
    "period, dual-mode indoor APs typically drop to LPI, and SP-only "
    "hardware cannot. Confirm your AP's behavior, and design so LPI "
    "coverage is survivable anyway.",
    "Survey for client talk-back, not just AP signal.",
    "40 MHz is a sound default channel width in either mode. Go wider "
    "when your grant and client population support it.",
    "Regulatory rules vary by country and change over time. Confirm "
    "current rules for your regulatory domain before deploying.",
]

ALL_PROMPTS = [g[0] for g in GATES] + [q[0] for q in QUESTIONS]


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

    total = len(ALL_PROMPTS)
    if args.answers:
        raw = [a.strip().lower() for a in args.answers.split(",")]
        if len(raw) != total or not set(raw) <= {"y", "n"}:
            parser.error(f"--answers needs {total} comma-separated "
                         "y/n values")
        answers = [a == "y" for a in raw]
    else:
        print("Answer for the site you are designing, not the ideal "
              "site. This tool assumes an indoor deployment where LPI "
              "is available.\n\nPrerequisites first:\n")
        answers = [ask(GATES[i][0]) for i in range(len(GATES))]
        print("\nNow the site itself:\n")
        answers += [ask(question) for question, _, _, _ in QUESTIONS]

    gate_answers = answers[:len(GATES)]
    blockers = [missing for answered_yes, (_, missing)
                in zip(gate_answers, GATES) if not answered_yes]

    scores = {"lpi": 0, "sp": 0}
    reasons = {"lpi": [], "sp": []}
    for answered_yes, (_, mode, weight, reason) in zip(
            answers[len(GATES):], QUESTIONS):
        if answered_yes:
            scores[mode] += weight
            reasons[mode].append(reason)

    print()
    if blockers:
        print("Recommendation: Low Power Indoor. Standard Power is "
              "blocked until you have:")
        for missing in blockers:
            print(f"  * {missing}")
        if scores["sp"] > scores["lpi"]:
            print("\nYour other answers lean Standard Power "
                  f"(score {scores['sp']} to {scores['lpi']}), so the "
                  "blockers above are worth investigating, in order, "
                  "before you finalize the design.")
        pick, other = "lpi", "sp"
    elif scores["sp"] > scores["lpi"]:
        pick, other = "sp", "lpi"
        print("Recommendation: Standard Power candidate "
              f"(score {scores['sp']} to {scores['lpi']}). Validate with "
              "a survey and a real AFC grant at your location before "
              "committing the channel plan.")
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

    if pick and reasons[pick]:
        print("\nWhy:")
        for reason in reasons[pick]:
            print(f"  * {reason}")
    if pick and reasons[other]:
        print("\nPulling the other way:")
        for reason in reasons[other]:
            print(f"  * {reason}")

    print("\nRegardless of mode:")
    for caveat in CAVEATS:
        print(f"  * {caveat}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
