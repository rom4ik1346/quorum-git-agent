const state = {
  analyses: [],
  selected: null,
};

const elements = {
  form: document.querySelector("#analysis-form"),
  input: document.querySelector("#repository"),
  analyzeButton: document.querySelector("#analyze-button"),
  demoButton: document.querySelector("#demo-button"),
  message: document.querySelector("#message"),
  healthScore: document.querySelector("#health-score"),
  scoreRing: document.querySelector("#score-ring"),
  scoreRingValue: document.querySelector("#score-ring-value"),
  analysisCount: document.querySelector("#analysis-count"),
  ciSuccess: document.querySelector("#ci-success"),
  openActions: document.querySelector("#open-actions"),
  repositoryName: document.querySelector("#repository-name"),
  repositoryLink: document.querySelector("#repository-link"),
  verdict: document.querySelector("#verdict"),
  summary: document.querySelector("#summary"),
  miniMetrics: document.querySelector("#mini-metrics"),
  languageList: document.querySelector("#language-list"),
  historyList: document.querySelector("#history-list"),
  riskList: document.querySelector("#risk-list"),
  actionList: document.querySelector("#action-list"),
  triageList: document.querySelector("#triage-list"),
};

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Request failed.");
  }
  return payload;
}

function setMessage(text = "", type = "") {
  elements.message.textContent = text;
  elements.message.className = `message ${type}`.trim();
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function renderOverview(overview, analysis) {
  elements.analysisCount.textContent = overview.analyses;
  elements.openActions.textContent = overview.open_actions;
  elements.healthScore.textContent = analysis.score;
  elements.scoreRingValue.textContent = analysis.score;
  elements.scoreRing.style.setProperty("--score", analysis.score);
  elements.ciSuccess.textContent =
    analysis.metrics.ci_success_rate === null ? "N/A" : `${analysis.metrics.ci_success_rate}%`;
}

function renderReport(analysis) {
  state.selected = analysis;
  elements.repositoryName.textContent = analysis.repository;
  elements.repositoryLink.href = analysis.repository_url || "#";
  elements.repositoryLink.hidden = !analysis.repository_url;
  elements.verdict.textContent = analysis.verdict;
  elements.summary.textContent = analysis.summary;

  const metrics = [
    ["Stars", analysis.metrics.stars],
    ["Forks", analysis.metrics.forks],
    ["Open issues", analysis.metrics.open_issues],
    ["Days since push", analysis.metrics.days_since_push],
  ];
  elements.miniMetrics.innerHTML = metrics
    .map(
      ([label, value]) => `
        <div class="mini-metric">
          <strong>${value}</strong>
          <span>${label}</span>
        </div>
      `,
    )
    .join("");

  elements.languageList.innerHTML = analysis.metrics.language_mix.length
    ? analysis.metrics.language_mix
        .map(
          (language) => `
            <div class="language-row">
              <span>${language.name}</span>
              <div class="language-track">
                <span style="width:${Math.max(language.share, 2)}%"></span>
              </div>
              <strong>${language.share}%</strong>
            </div>
          `,
        )
        .join("")
    : '<div class="empty-state">No language data available.</div>';

  elements.riskList.innerHTML = analysis.risks
    .map(
      (risk) => `
        <div class="stack-item">
          <div class="stack-top">
            <strong>${risk.title}</strong>
            <span class="severity-pill ${risk.severity}">${risk.severity}</span>
          </div>
          <p>${risk.detail}</p>
        </div>
      `,
    )
    .join("");

  elements.actionList.innerHTML = analysis.actions
    .map(
      (action) => `
        <div class="stack-item">
          <div class="stack-top">
            <strong>${action.title}</strong>
            <span class="priority-pill ${action.priority}">${action.priority}</span>
          </div>
          <p>${action.why}</p>
        </div>
      `,
    )
    .join("");

  elements.triageList.innerHTML = analysis.triaged_issues.length
    ? analysis.triaged_issues
        .map(
          (issue) => `
            <a class="triage-row" href="${issue.url || "#"}" target="_blank" rel="noreferrer">
              <span class="issue-number">#${issue.number}</span>
              <strong class="issue-title">${issue.title}</strong>
              <span class="priority-pill ${issue.priority}">${issue.priority}</span>
              <span class="issue-meta">${issue.age_days}d · ${issue.comments} msg</span>
            </a>
          `,
        )
        .join("")
    : '<div class="empty-state">No open issues were returned for this repository.</div>';
}

function renderHistory() {
  elements.historyList.innerHTML = state.analyses
    .slice(0, 8)
    .map(
      (analysis) => `
        <button class="history-item" data-analysis-id="${analysis.id}" type="button">
          <span class="history-top">
            <strong>${analysis.repository}</strong>
            <span class="score-pill">${analysis.score}</span>
          </span>
          <small>${formatDate(analysis.created_at)} · ${analysis.verdict}</small>
        </button>
      `,
    )
    .join("");

  elements.historyList.querySelectorAll("[data-analysis-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const analysis = state.analyses.find((item) => item.id === button.dataset.analysisId);
      if (analysis) {
        renderReport(analysis);
        loadOverview(analysis);
      }
    });
  });
}

async function loadOverview(analysis = state.selected) {
  const overview = await request("/api/overview");
  if (analysis) renderOverview(overview, analysis);
}

async function refresh(preferredAnalysis = null) {
  state.analyses = await request("/api/analyses");
  const analysis = preferredAnalysis || state.analyses[0];
  renderHistory();
  if (analysis) {
    renderReport(analysis);
    await loadOverview(analysis);
  }
}

async function createAnalysis(repository) {
  elements.analyzeButton.disabled = true;
  setMessage(`Analyzing ${repository}…`);
  try {
    const analysis = await request("/api/analyses", {
      method: "POST",
      body: JSON.stringify({ repository }),
    });
    await refresh(analysis);
    setMessage(`Analysis saved for ${analysis.repository}.`);
    elements.form.reset();
  } catch (error) {
    setMessage(error.message, "error");
  } finally {
    elements.analyzeButton.disabled = false;
  }
}

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  const repository = elements.input.value.trim();
  if (repository) createAnalysis(repository);
});

elements.demoButton.addEventListener("click", async () => {
  setMessage("Creating a fresh demo report…");
  try {
    const analysis = await request("/api/analyses/demo", { method: "POST" });
    await refresh(analysis);
    setMessage("Demo report created.");
  } catch (error) {
    setMessage(error.message, "error");
  }
});

refresh().catch((error) => setMessage(error.message, "error"));

