-- Release readiness queue.
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
