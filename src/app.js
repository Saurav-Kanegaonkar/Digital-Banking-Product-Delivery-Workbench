const state = {
  payload: null,
  surface: "readiness",
};

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const percent = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 0,
});

function statusClass(status) {
  return status.toLowerCase();
}

function metricCard(label, value, hint, tone = "") {
  return `
    <article class="metric-card ${tone}">
      <span>${label}</span>
      <strong>${value}</strong>
      <em>${hint}</em>
    </article>
  `;
}

function pill(text, tone = "") {
  return `<span class="pill ${tone}">${text}</span>`;
}

function renderMetrics() {
  const { summary } = state.payload;
  document.querySelector("#metricGrid").innerHTML = [
    metricCard("Blocked epics", summary.blocked_epics, `${summary.watch_epics} on watch`, "danger"),
    metricCard("Readiness", `${summary.avg_readiness}/100`, `${summary.ready_epics} ready`, "neutral"),
    metricCard("UAT pass rate", percent.format(summary.avg_uat_pass_rate), `${summary.uat_case_count} cases`, "success"),
    metricCard("P1/P2 defects", `${summary.p1_defects}/${summary.p2_defects}`, "high-severity backlog", "warning"),
    metricCard("Modeled value at risk", currency.format(summary.value_at_risk), `${summary.story_count} stories`, "neutral"),
  ].join("");

  const top = summary.top_epic;
  document.querySelector("#releaseCallout").innerHTML = `
    <span>Highest priority</span>
    <strong>${top.capability}</strong>
    <em>${top.next_decision}</em>
  `;
}

function renderReadiness() {
  const rows = state.payload.releaseQueue.slice(0, 10);
  document.querySelector("#queueCount").textContent = `${rows.length} ranked capabilities`;
  document.querySelector("#releaseQueue").innerHTML = rows
    .map((row) => `
      <tr>
        <td>
          <button class="link-button" data-epic="${row.epic_id}" type="button">${row.capability}</button>
          <small>${row.module}</small>
        </td>
        <td>${pill(row.release_status, statusClass(row.release_status))}</td>
        <td>${row.readiness_score}/100</td>
        <td>${percent.format(row.uat_pass_rate)}</td>
        <td>${row.p1_defects}/${row.p2_defects}</td>
        <td>${row.next_decision}</td>
      </tr>
    `)
    .join("");

  renderTopBlocker(rows[0].epic_id);
}

function renderTopBlocker(epicId) {
  const epic = state.payload.epics.find((item) => item.epic_id === epicId);
  const action = state.payload.actions.find((item) => item.epic_id === epicId);
  const stories = state.payload.stories.filter((story) => story.epic_id === epicId);
  const worstStory = stories.sort((a, b) => a.readiness_score - b.readiness_score)[0];

  document.querySelector("#topBlocker").innerHTML = `
    <div class="detail-row">
      <span>Capability</span>
      <strong>${epic.capability}</strong>
    </div>
    <div class="detail-row">
      <span>Release train</span>
      <strong>${epic.release_train}</strong>
    </div>
    <div class="detail-row">
      <span>Product decision</span>
      <strong>${action.recommended_action}</strong>
    </div>
    <div class="detail-row">
      <span>Worst story</span>
      <strong>${worstStory.story_id}, ${worstStory.readiness_score}/100</strong>
    </div>
    <p class="narrative">${worstStory.sample_acceptance_criteria}</p>
  `;
}

function renderTraceability() {
  const rows = state.payload.traceability.slice(0, 12);
  document.querySelector("#traceabilityRows").innerHTML = rows
    .map((row) => `
      <tr>
        <td><button class="link-button" data-story="${row.story_id}" type="button">${row.story_id}</button></td>
        <td>${row.capability}</td>
        <td>${row.acceptance_criteria_count}</td>
        <td>${row.uat_test_cases}</td>
        <td>${row.coverage_gap}</td>
        <td>${pill(row.signoff_status, row.signoff_status === "Signed" ? "ready" : "watch")}</td>
      </tr>
    `)
    .join("");

  renderStoryDetail(rows[0].story_id);
}

function renderStoryDetail(storyId) {
  const story = state.payload.stories.find((item) => item.story_id === storyId);
  const epic = state.payload.epics.find((item) => item.epic_id === story.epic_id);
  const cases = state.payload.testCases.filter((item) => item.story_id === storyId).slice(0, 4);

  document.querySelector("#storyDetail").innerHTML = `
    <div class="detail-row">
      <span>Epic</span>
      <strong>${epic.capability}</strong>
    </div>
    <div class="detail-row">
      <span>User story</span>
      <strong>${story.user_story}</strong>
    </div>
    <p class="criteria">${story.sample_acceptance_criteria}</p>
    <div class="mini-list">
      ${cases.map((item) => `<span>${item.test_case_id}: ${item.uat_status}</span>`).join("")}
    </div>
  `;
}

function renderTriage() {
  const rows = state.payload.defectTriage.slice(0, 12);
  document.querySelector("#defectRows").innerHTML = rows
    .map((row) => `
      <tr>
        <td>${row.defect_id}<small>${row.defect_type}</small></td>
        <td>${row.capability}</td>
        <td>${pill(row.severity, row.severity.toLowerCase())}</td>
        <td>${row.owner}</td>
        <td>${row.days_open}</td>
        <td>${row.workflow_impact}</td>
      </tr>
    `)
    .join("");

  const topEpic = rows[0].capability;
  const epic = state.payload.epics.find((item) => item.capability === topEpic);
  const ceremonies = state.payload.ceremonies.filter((item) => item.epic_id === epic.epic_id);
  const actions = state.payload.actions.filter((item) => item.epic_id === epic.epic_id);

  document.querySelector("#ceremonyPacket").innerHTML = `
    ${ceremonies.map((item) => `
      <div class="packet-item">
        <span>${item.ceremony}</span>
        <strong>${item.decision_needed}</strong>
        <em>${item.status}, due ${item.due_date}</em>
      </div>
    `).join("")}
    ${actions.map((item) => `
      <div class="packet-item accent">
        <span>${item.priority} action</span>
        <strong>${item.recommended_action}</strong>
        <em>${item.expected_outcome}, ${item.effort_hours} hours</em>
      </div>
    `).join("")}
  `;
}

function setSurface(surface) {
  state.surface = surface;
  document.querySelectorAll(".surface-tabs button").forEach((button) => {
    button.classList.toggle("active", button.dataset.surface === surface);
  });
  document.querySelectorAll(".surface").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `${surface}Surface`);
  });
}

function bindEvents() {
  document.querySelector(".surface-tabs").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-surface]");
    if (button) setSurface(button.dataset.surface);
  });

  document.body.addEventListener("click", (event) => {
    const epicButton = event.target.closest("button[data-epic]");
    if (epicButton) renderTopBlocker(epicButton.dataset.epic);

    const storyButton = event.target.closest("button[data-story]");
    if (storyButton) renderStoryDetail(storyButton.dataset.story);
  });
}

async function init() {
  const response = await fetch("analysis/outputs/app_payload.json");
  state.payload = await response.json();
  renderMetrics();
  renderReadiness();
  renderTraceability();
  renderTriage();
  bindEvents();
}

init();
