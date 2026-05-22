# Data Sources

This project uses synthetic, workflow-shaped data because real digital banking product backlogs, UAT scripts, defect logs, sprint artifacts, and release-readiness notes are normally confidential.

The generator uses a fixed random seed for reproducibility. It models common digital banking product delivery structures:

- Capabilities across onboarding, login and security, transfers, bill pay, card controls, alerts, statements, profile servicing, dispute intake, and small-business entitlements.
- User stories with personas, acceptance criteria counts, data dependencies, grooming quality, UAT pass rate, defect exposure, and signoff status.
- UAT cases with channel, owner, last run date, and pass, failed, or blocked status.
- Defects with severity, owner, status, days open, workflow impact, and triage score inputs.
- Sprint ceremonies and recommended actions that mirror backlog refinement, sprint planning, UAT triage, and release signoff.

Files:

- `epics.csv`: Product capabilities at release-readiness grain.
- `user_stories.csv`: User stories with acceptance criteria, readiness, UAT coverage, and signoff fields.
- `uat_test_cases.csv`: UAT scenarios linked to user stories.
- `defects.csv`: Defect log linked to stories and epics.
- `sprint_ceremonies.csv`: Ceremony decisions and due dates.
- `okr_metrics.csv`: Product performance metrics tied to epics.
- `recommended_actions.csv`: Owner-ready next steps.
