# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `data/epics.csv` | Digital banking capability | Release train, squad, compliance touchpoint, readiness, UAT pass rate, defects, and modeled value at risk. |
| `data/user_stories.csv` | User story | Persona, user story text, sample acceptance criteria, grooming score, UAT coverage, defects, and business signoff. |
| `data/uat_test_cases.csv` | UAT test case | Scenario, channel, UAT status, business owner, and last run date. |
| `data/defects.csv` | Defect | Severity, defect type, workflow impact, owner, status, days open, and impact points. |
| `data/sprint_ceremonies.csv` | Ceremony action | Backlog refinement and UAT triage decisions, facilitator, due date, and status. |
| `data/okr_metrics.csv` | OKR metric | Baseline, target, current value, and confidence for product performance metrics. |
| `data/recommended_actions.csv` | Action | Product analyst recommendation, owner, expected outcome, effort, and priority. |
| `analysis/outputs/release_readiness.csv` | Epic | Ranked release-readiness queue used by the cockpit surface. |
| `analysis/outputs/requirements_traceability.csv` | User story | Requirements to UAT coverage and signoff gaps. |
| `analysis/outputs/defect_triage.csv` | Defect | Ranked remediation queue used by the triage surface. |
| `analysis/outputs/app_payload.json` | Application payload | Static web-app data bundle. |
