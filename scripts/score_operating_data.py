import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "analysis" / "outputs"

RNG = random.Random(42)

CAPABILITIES = [
    {
        "capability": "Digital onboarding",
        "module": "Account opening",
        "persona": "New checking customer",
        "okr": "Activation",
        "base_value": 92,
        "risk": 0.82,
        "stories": [
            "prefill verified identity data",
            "save an unfinished application",
            "show missing-document reasons",
        ],
    },
    {
        "capability": "Login and step-up security",
        "module": "Security",
        "persona": "Mobile banking customer",
        "okr": "Trust",
        "base_value": 88,
        "risk": 0.78,
        "stories": [
            "step up high-risk sessions",
            "recover access with verified contact data",
            "explain failed authentication attempts",
        ],
    },
    {
        "capability": "Internal and external transfers",
        "module": "Money movement",
        "persona": "Everyday banking customer",
        "okr": "Transaction completion",
        "base_value": 96,
        "risk": 0.9,
        "stories": [
            "schedule recurring transfers",
            "surface transfer limits before submit",
            "send transfer confirmation alerts",
        ],
    },
    {
        "capability": "Bill pay enrollment",
        "module": "Payments",
        "persona": "Household bill payer",
        "okr": "Self-service",
        "base_value": 84,
        "risk": 0.7,
        "stories": [
            "add a new payee with address validation",
            "review pending bill pay payments",
            "edit payment delivery date",
        ],
    },
    {
        "capability": "Debit card controls",
        "module": "Cards",
        "persona": "Cardholder",
        "okr": "Self-service",
        "base_value": 86,
        "risk": 0.74,
        "stories": [
            "freeze and unfreeze a debit card",
            "set travel notice rules",
            "view merchant-level authorization declines",
        ],
    },
    {
        "capability": "Account alerts",
        "module": "Notifications",
        "persona": "Mobile banking customer",
        "okr": "Trust",
        "base_value": 76,
        "risk": 0.58,
        "stories": [
            "configure low-balance alerts",
            "confirm alert delivery channel",
            "pause duplicate notifications",
        ],
    },
    {
        "capability": "Statements and documents",
        "module": "Documents",
        "persona": "Digital servicing customer",
        "okr": "Self-service",
        "base_value": 72,
        "risk": 0.52,
        "stories": [
            "download prior statements",
            "enroll in paperless delivery",
            "search tax documents by year",
        ],
    },
    {
        "capability": "Profile and contact servicing",
        "module": "Profile",
        "persona": "Digital servicing customer",
        "okr": "Servicing cost",
        "base_value": 74,
        "risk": 0.55,
        "stories": [
            "update preferred phone number",
            "confirm mailing address changes",
            "route sensitive updates to review",
        ],
    },
    {
        "capability": "Dispute intake",
        "module": "Claims",
        "persona": "Cardholder with transaction issue",
        "okr": "Trust",
        "base_value": 90,
        "risk": 0.86,
        "stories": [
            "submit a debit card dispute",
            "attach dispute documentation",
            "track provisional credit status",
        ],
    },
    {
        "capability": "Small-business entitlements",
        "module": "Business banking",
        "persona": "Small-business admin",
        "okr": "Commercial readiness",
        "base_value": 94,
        "risk": 0.88,
        "stories": [
            "assign payment approval roles",
            "set dual-control thresholds",
            "audit user permission changes",
        ],
    },
]

SEVERITIES = ["P1", "P2", "P3", "P4"]
DEFECT_TYPES = [
    "acceptance criteria gap",
    "API mapping issue",
    "accessibility miss",
    "audit trail gap",
    "channel parity gap",
    "data validation issue",
    "edge-case workflow break",
    "error message ambiguity",
    "integration timing issue",
    "regression in mobile layout",
]


def clamp(value, low, high):
    return max(low, min(high, value))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def status_from_scores(readiness_score, p1_count, p2_count, uat_pass_rate):
    if p1_count > 0 or readiness_score < 62 or uat_pass_rate < 0.62:
        return "Blocked"
    if p2_count > 2 or readiness_score < 78 or uat_pass_rate < 0.78:
        return "Watch"
    return "Ready"


def build_data():
    epics = []
    stories = []
    test_cases = []
    defects = []
    ceremonies = []
    okr_rows = []
    actions = []

    for index, capability in enumerate(CAPABILITIES, start=1):
        epic_id = f"EP{index:03d}"
        release_train = ["Mobile Release Train", "Servicing Release Train", "Payments Release Train"][index % 3]
        squad = ["Journey Core", "Money Movement", "Servicing Enablement", "Digital Trust"][index % 4]
        target_sprint = f"Sprint {7 + index // 2}"
        business_owner = ["Digital PO", "Operations Lead", "Risk Partner", "Contact Center Lead"][index % 4]
        compliance_touchpoint = "Yes" if capability["risk"] > 0.72 or index in {1, 2, 9, 10} else "No"

        story_ids = []
        story_scores = []
        story_defect_counts = []
        story_p1 = 0
        story_p2 = 0
        story_test_total = 0
        story_test_passed = 0
        uncovered = 0
        signoffs = 0
        total_acceptance = 0

        for story_index, story_action in enumerate(capability["stories"], start=1):
            story_id = f"US{index:03d}-{story_index}"
            story_ids.append(story_id)
            acceptance_count = RNG.choice([3, 4, 4, 5])
            total_acceptance += acceptance_count
            points = RNG.choice([3, 5, 5, 8])
            risk_noise = RNG.uniform(-0.08, 0.15)
            requirement_risk = clamp(capability["risk"] + risk_noise, 0.35, 0.98)
            grooming_score = round(clamp(RNG.gauss(82 - requirement_risk * 16, 7), 48, 98), 1)
            acceptance_quality = round(clamp(RNG.gauss(84 - requirement_risk * 10, 6), 50, 99), 1)
            data_dependency = RNG.choice(["Core banking", "Cards processor", "Fraud service", "CRM", "Document store", "Notification hub"])
            workflow = RNG.choice(["happy path", "exception path", "servicing path", "admin path", "audit path"])
            owner = RNG.choice(["Product owner", "Business analyst", "QA lead", "Engineering lead"])

            test_count = acceptance_count + RNG.choice([0, 1, 1, 2])
            passed = 0
            blocked = 0
            failed = 0

            for test_index in range(1, test_count + 1):
                test_id = f"TC{index:03d}-{story_index}-{test_index}"
                probability_fail = 0.08 + requirement_risk * 0.12
                probability_block = 0.04 + requirement_risk * 0.08
                roll = RNG.random()
                if roll < probability_block:
                    uat_status = "Blocked"
                    blocked += 1
                elif roll < probability_block + probability_fail:
                    uat_status = "Failed"
                    failed += 1
                else:
                    uat_status = "Passed"
                    passed += 1

                test_cases.append(
                    {
                        "test_case_id": test_id,
                        "story_id": story_id,
                        "scenario": f"{workflow.title()} validation for {story_action}",
                        "channel": RNG.choice(["Mobile", "Online", "Both"]),
                        "uat_status": uat_status,
                        "business_owner": business_owner,
                        "last_run": f"2026-05-{RNG.randint(6, 20):02d}",
                    }
                )

            defect_count = failed + blocked + (1 if RNG.random() < requirement_risk * 0.35 else 0)
            p1_count = 0
            p2_count = 0
            for defect_index in range(1, defect_count + 1):
                if requirement_risk > 0.83 and RNG.random() < 0.15:
                    severity = "P1"
                elif requirement_risk > 0.68 and RNG.random() < 0.38:
                    severity = "P2"
                else:
                    severity = RNG.choice(["P2", "P3", "P3", "P4"])
                p1_count += 1 if severity == "P1" else 0
                p2_count += 1 if severity == "P2" else 0
                impact = round(RNG.uniform(1.0, 5.0) * capability["base_value"] * (1.6 if severity in {"P1", "P2"} else 0.8), 1)
                defects.append(
                    {
                        "defect_id": f"DF{index:03d}-{story_index}-{defect_index}",
                        "story_id": story_id,
                        "epic_id": epic_id,
                        "module": capability["module"],
                        "severity": severity,
                        "defect_type": RNG.choice(DEFECT_TYPES),
                        "workflow_impact": RNG.choice(["release blocker", "UAT retest needed", "customer friction", "operations workaround", "documentation update"]),
                        "owner": RNG.choice(["Engineering", "QA", "Product", "Risk", "Vendor"]),
                        "status": RNG.choice(["Open", "Open", "In remediation", "Retest scheduled", "Deferred"]),
                        "days_open": RNG.randint(1, 18),
                        "impact_points": impact,
                    }
                )

            coverage_rate = round(min(1.0, test_count / max(1, acceptance_count + 1)), 3)
            pass_rate = round(passed / max(1, test_count), 3)
            readiness_score = round(
                clamp(
                    35 * pass_rate
                    + 22 * coverage_rate
                    + 15 * (grooming_score / 100)
                    + 14 * (acceptance_quality / 100)
                    + 14 * (1 - requirement_risk)
                    - p1_count * 18
                    - p2_count * 5,
                    0,
                    100,
                ),
                1,
            )
            signoff_status = "Signed" if readiness_score >= 78 and p1_count == 0 else ("Pending" if readiness_score >= 62 else "Not ready")
            signoffs += 1 if signoff_status == "Signed" else 0
            story_scores.append(readiness_score)
            story_defect_counts.append(defect_count)
            story_p1 += p1_count
            story_p2 += p2_count
            story_test_total += test_count
            story_test_passed += passed
            uncovered += max(0, acceptance_count - test_count)

            stories.append(
                {
                    "story_id": story_id,
                    "epic_id": epic_id,
                    "module": capability["module"],
                    "persona": capability["persona"],
                    "user_story": f"As a {capability['persona'].lower()}, I need to {story_action} so I can complete banking tasks without calling support.",
                    "acceptance_criteria_count": acceptance_count,
                    "sample_acceptance_criteria": f"Given verified account context, when the user attempts to {story_action}, then the experience confirms eligibility, errors, and audit logging before completion.",
                    "story_points": points,
                    "sprint": target_sprint,
                    "owner": owner,
                    "data_dependency": data_dependency,
                    "grooming_score": grooming_score,
                    "acceptance_quality": acceptance_quality,
                    "uat_test_cases": test_count,
                    "uat_pass_rate": pass_rate,
                    "p1_defects": p1_count,
                    "p2_defects": p2_count,
                    "signoff_status": signoff_status,
                    "readiness_score": readiness_score,
                }
            )

        epic_pass_rate = round(story_test_passed / max(1, story_test_total), 3)
        epic_readiness = round(sum(story_scores) / len(story_scores), 1)
        epic_status = status_from_scores(epic_readiness, story_p1, story_p2, epic_pass_rate)
        epic_defects = sum(story_defect_counts)
        value_at_risk = int(capability["base_value"] * (1 + capability["risk"]) * (1 + epic_defects / 12) * 10000)

        epics.append(
            {
                "epic_id": epic_id,
                "capability": capability["capability"],
                "module": capability["module"],
                "release_train": release_train,
                "squad": squad,
                "target_sprint": target_sprint,
                "business_owner": business_owner,
                "compliance_touchpoint": compliance_touchpoint,
                "okr": capability["okr"],
                "story_count": len(story_ids),
                "acceptance_criteria": total_acceptance,
                "uat_cases": story_test_total,
                "uat_pass_rate": epic_pass_rate,
                "p1_defects": story_p1,
                "p2_defects": story_p2,
                "total_defects": epic_defects,
                "signed_stories": signoffs,
                "readiness_score": epic_readiness,
                "release_status": epic_status,
                "value_at_risk": value_at_risk,
            }
        )

        action_type = "Escalate defect remediation" if epic_status == "Blocked" else ("Tighten UAT coverage" if epic_status == "Watch" else "Prepare release signoff")
        actions.append(
            {
                "action_id": f"ACT{index:03d}",
                "epic_id": epic_id,
                "recommended_action": action_type,
                "owner": business_owner,
                "expected_outcome": RNG.choice(
                    [
                        "clear release gate",
                        "reduce retest loops",
                        "close acceptance criteria gaps",
                        "protect customer-facing launch quality",
                    ]
                ),
                "effort_hours": RNG.randint(6, 28),
                "priority": "High" if epic_status == "Blocked" else ("Medium" if epic_status == "Watch" else "Normal"),
            }
        )

        ceremonies.extend(
            [
                {
                    "ceremony_id": f"CER{index:03d}-1",
                    "epic_id": epic_id,
                    "ceremony": "Backlog refinement",
                    "decision_needed": "Confirm acceptance criteria and data dependencies",
                    "facilitator": "Product analyst",
                    "due_date": f"2026-05-{RNG.randint(22, 28):02d}",
                    "status": "Scheduled" if epic_status != "Ready" else "Complete",
                },
                {
                    "ceremony_id": f"CER{index:03d}-2",
                    "epic_id": epic_id,
                    "ceremony": "UAT triage",
                    "decision_needed": "Resolve high-severity defects and retest path",
                    "facilitator": "QA lead",
                    "due_date": f"2026-05-{RNG.randint(22, 30):02d}",
                    "status": "Needs escalation" if story_p1 > 0 or story_p2 > 1 else "Scheduled",
                },
            ]
        )

        okr_rows.append(
            {
                "okr": capability["okr"],
                "epic_id": epic_id,
                "metric": RNG.choice(["Digital completion", "Call deflection", "First-time success", "Retest cycle time", "Release predictability"]),
                "baseline": round(RNG.uniform(54, 82), 1),
                "target": round(RNG.uniform(76, 94), 1),
                "current": round(RNG.uniform(58, 89) - story_p1 * 4 - story_p2 * 1.5, 1),
                "confidence": RNG.choice(["High", "Medium", "Medium", "Low"]),
            }
        )

    return epics, stories, test_cases, defects, ceremonies, okr_rows, actions


def analyze(epics, stories, test_cases, defects, ceremonies, okr_rows, actions):
    story_by_id = {row["story_id"]: row for row in stories}
    epic_by_id = {row["epic_id"]: row for row in epics}
    defects_by_epic = defaultdict(list)
    for defect in defects:
        defects_by_epic[defect["epic_id"]].append(defect)

    release_queue = []
    for epic in epics:
        severity_penalty = epic["p1_defects"] * 30 + epic["p2_defects"] * 10 + epic["total_defects"] * 2
        coverage_gap = max(0, epic["acceptance_criteria"] - epic["uat_cases"])
        priority_score = round(
            (100 - epic["readiness_score"])
            + severity_penalty
            + coverage_gap * 3
            + math.log1p(epic["value_at_risk"] / 10000),
            1,
        )
        release_queue.append(
            {
                "epic_id": epic["epic_id"],
                "capability": epic["capability"],
                "module": epic["module"],
                "release_status": epic["release_status"],
                "readiness_score": epic["readiness_score"],
                "uat_pass_rate": epic["uat_pass_rate"],
                "p1_defects": epic["p1_defects"],
                "p2_defects": epic["p2_defects"],
                "value_at_risk": epic["value_at_risk"],
                "priority_score": priority_score,
                "next_decision": "Hold release and run triage" if epic["release_status"] == "Blocked" else ("Retest and confirm signoff" if epic["release_status"] == "Watch" else "Move to launch checklist"),
            }
        )

    release_queue.sort(key=lambda row: row["priority_score"], reverse=True)

    traceability = []
    for story in stories:
        gap = max(0, int(story["acceptance_criteria_count"]) - int(story["uat_test_cases"]))
        traceability.append(
            {
                "story_id": story["story_id"],
                "epic_id": story["epic_id"],
                "capability": epic_by_id[story["epic_id"]]["capability"],
                "module": story["module"],
                "acceptance_criteria_count": story["acceptance_criteria_count"],
                "uat_test_cases": story["uat_test_cases"],
                "coverage_gap": gap,
                "uat_pass_rate": story["uat_pass_rate"],
                "p1_defects": story["p1_defects"],
                "p2_defects": story["p2_defects"],
                "signoff_status": story["signoff_status"],
                "readiness_score": story["readiness_score"],
            }
        )
    traceability.sort(key=lambda row: (row["coverage_gap"], row["p1_defects"], row["p2_defects"], 100 - row["readiness_score"]), reverse=True)

    defect_triage = []
    severity_weight = {"P1": 100, "P2": 65, "P3": 30, "P4": 12}
    for defect in defects:
        story = story_by_id[defect["story_id"]]
        epic = epic_by_id[defect["epic_id"]]
        triage_score = round(
            severity_weight[defect["severity"]]
            + defect["impact_points"]
            + max(0, defect["days_open"] - 5) * 2
            + (100 - story["readiness_score"]) * 0.25,
            1,
        )
        defect_triage.append(
            {
                "defect_id": defect["defect_id"],
                "story_id": defect["story_id"],
                "capability": epic["capability"],
                "module": defect["module"],
                "severity": defect["severity"],
                "defect_type": defect["defect_type"],
                "workflow_impact": defect["workflow_impact"],
                "owner": defect["owner"],
                "status": defect["status"],
                "days_open": defect["days_open"],
                "triage_score": triage_score,
            }
        )
    defect_triage.sort(key=lambda row: row["triage_score"], reverse=True)

    summary = {
        "epic_count": len(epics),
        "story_count": len(stories),
        "uat_case_count": len(test_cases),
        "defect_count": len(defects),
        "blocked_epics": sum(1 for epic in epics if epic["release_status"] == "Blocked"),
        "watch_epics": sum(1 for epic in epics if epic["release_status"] == "Watch"),
        "ready_epics": sum(1 for epic in epics if epic["release_status"] == "Ready"),
        "avg_readiness": round(sum(epic["readiness_score"] for epic in epics) / len(epics), 1),
        "avg_uat_pass_rate": round(sum(epic["uat_pass_rate"] for epic in epics) / len(epics), 3),
        "p1_defects": sum(epic["p1_defects"] for epic in epics),
        "p2_defects": sum(epic["p2_defects"] for epic in epics),
        "value_at_risk": sum(epic["value_at_risk"] for epic in epics),
        "top_epic": release_queue[0],
        "defects_by_severity": dict(Counter(defect["severity"] for defect in defects)),
        "statuses": dict(Counter(epic["release_status"] for epic in epics)),
    }

    app_payload = {
        "summary": summary,
        "releaseQueue": release_queue,
        "traceability": traceability,
        "defectTriage": defect_triage,
        "epics": epics,
        "stories": stories,
        "testCases": test_cases,
        "ceremonies": ceremonies,
        "okrs": okr_rows,
        "actions": actions,
    }

    return summary, release_queue, traceability, defect_triage, app_payload


def write_docs(summary, release_queue, traceability, defect_triage):
    top = release_queue[0]
    executive_findings = f"""# Executive Findings

## What I analyzed

This artifact models a digital banking product analyst workflow across {summary['epic_count']} epics, {summary['story_count']} user stories, {summary['uat_case_count']} UAT test cases, and {summary['defect_count']} defects.

## Findings

- {summary['blocked_epics']} epics are blocked and {summary['watch_epics']} are on watch, which gives the product analyst a focused release-readiness queue.
- Average readiness is {summary['avg_readiness']} out of 100, with an average UAT pass rate of {summary['avg_uat_pass_rate']:.1%}.
- The highest-priority release risk is {top['capability']} in {top['module']}, with {top['p1_defects']} P1 defects, {top['p2_defects']} P2 defects, and ${top['value_at_risk']:,} in modeled value at risk.
- The largest analyst leverage point is requirements traceability: stories with weak acceptance coverage or unresolved high-severity defects should be pulled into refinement and UAT triage before launch.

## Recommendation

Use the release queue as the weekly decision artifact. For blocked capabilities, hold release signoff, clarify acceptance criteria, assign defect owners, and schedule retest in the next UAT triage ceremony. For watch capabilities, confirm business-owner signoff and close coverage gaps before moving to launch checklist.
"""
    (ROOT / "analysis" / "executive_findings.md").write_text(executive_findings)

    analysis_plan = """# Analysis Plan

1. Generate a digital banking backlog at epic, user-story, acceptance-criteria, UAT, defect, and ceremony grain.
2. Score user-story readiness using UAT pass rate, test coverage, grooming quality, acceptance quality, requirement risk, and high-severity defects.
3. Roll story readiness into epic-level release status.
4. Build a release-readiness queue that combines readiness gap, defect severity, coverage gap, and modeled value at risk.
5. Build traceability and defect-triage outputs that a product analyst can use in backlog refinement, sprint planning, UAT triage, and stakeholder readouts.
"""
    (ROOT / "analysis" / "analysis_plan.md").write_text(analysis_plan)

    sql_checks = """-- Release readiness queue.
select
  epic_id,
  capability,
  module,
  readiness_score,
  uat_pass_rate,
  p1_defects,
  p2_defects,
  value_at_risk
from release_readiness
where release_status in ('Blocked', 'Watch')
order by p1_defects desc, p2_defects desc, readiness_score asc;

-- Requirements to UAT traceability gaps.
select
  story_id,
  epic_id,
  acceptance_criteria_count,
  uat_test_cases,
  coverage_gap,
  signoff_status
from requirements_traceability
where coverage_gap > 0 or signoff_status <> 'Signed'
order by coverage_gap desc, readiness_score asc;

-- Defect remediation triage.
select
  defect_id,
  story_id,
  module,
  severity,
  owner,
  days_open,
  triage_score
from defect_triage
where severity in ('P1', 'P2')
order by triage_score desc;
"""
    (ROOT / "analysis" / "sql_checks.sql").write_text(sql_checks)


def main():
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    epics, stories, test_cases, defects, ceremonies, okr_rows, actions = build_data()
    summary, release_queue, traceability, defect_triage, app_payload = analyze(
        epics, stories, test_cases, defects, ceremonies, okr_rows, actions
    )

    write_csv(DATA_DIR / "epics.csv", epics, list(epics[0].keys()))
    write_csv(DATA_DIR / "user_stories.csv", stories, list(stories[0].keys()))
    write_csv(DATA_DIR / "uat_test_cases.csv", test_cases, list(test_cases[0].keys()))
    write_csv(DATA_DIR / "defects.csv", defects, list(defects[0].keys()))
    write_csv(DATA_DIR / "sprint_ceremonies.csv", ceremonies, list(ceremonies[0].keys()))
    write_csv(DATA_DIR / "okr_metrics.csv", okr_rows, list(okr_rows[0].keys()))
    write_csv(DATA_DIR / "recommended_actions.csv", actions, list(actions[0].keys()))

    write_csv(OUTPUT_DIR / "release_readiness.csv", release_queue, list(release_queue[0].keys()))
    write_csv(OUTPUT_DIR / "requirements_traceability.csv", traceability, list(traceability[0].keys()))
    write_csv(OUTPUT_DIR / "defect_triage.csv", defect_triage, list(defect_triage[0].keys()))
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUTPUT_DIR / "app_payload.json").write_text(json.dumps(app_payload, indent=2))

    write_docs(summary, release_queue, traceability, defect_triage)

    print(f"Generated {len(epics)} epics, {len(stories)} stories, {len(test_cases)} UAT cases, and {len(defects)} defects.")
    print(f"Top release risk: {summary['top_epic']['capability']} ({summary['top_epic']['release_status']}).")


if __name__ == "__main__":
    main()
