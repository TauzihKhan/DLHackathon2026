const API_BASE = window.localStorage.getItem('apiBase') || 'http://localhost:8000';

const nodes = {
  studentId: document.getElementById('studentId'),
  refreshBtn: document.getElementById('refreshBtn'),
  xpValue: document.getElementById('xpValue'),
  masteredValue: document.getElementById('masteredValue'),
  riskValue: document.getElementById('riskValue'),
  masteryChart: document.getElementById('masteryChart'),
  weakTopicsList: document.getElementById('weakTopicsList'),
  recommendation: document.getElementById('recommendation'),
  reviewMeta: document.getElementById('reviewMeta'),
  reviewQueueList: document.getElementById('reviewQueueList'),
  sourceNote: document.getElementById('sourceNote')
};

const mockState = {
  learner_id: 'student-001',
  xp_total: 1240,
  updated_at: '2026-03-03T10:00:00Z',
  subtopics: [
    {
      module_id: 'math',
      topic_id: 'Algebra',
      subtopic_id: 'Quadratics',
      mastery: 0.82,
      confidence: 0.77,
      xp: 420,
      decay_risk_score: 0.12,
      last_interaction_at: '2026-03-03T09:20:00Z',
      attempts: 15,
      correct_attempts: 12
    },
    {
      module_id: 'math',
      topic_id: 'Calculus',
      subtopic_id: 'Integration',
      mastery: 0.42,
      confidence: 0.32,
      xp: 260,
      decay_risk_score: 0.64,
      last_interaction_at: '2026-02-20T09:20:00Z',
      attempts: 11,
      correct_attempts: 4
    },
    {
      module_id: 'math',
      topic_id: 'Probability',
      subtopic_id: 'Conditional Probability',
      mastery: 0.58,
      confidence: 0.5,
      xp: 310,
      decay_risk_score: 0.28,
      last_interaction_at: '2026-03-01T09:20:00Z',
      attempts: 13,
      correct_attempts: 7
    }
  ]
};

const mockInsight = {
  learner_id: 'student-001',
  generated_at: '2026-03-03T10:00:00Z',
  weak_subtopics: ['Integration'],
  priority_subtopic_id: 'Integration',
  recommended_action: 'Review Integration now with a 5-question quick recap.',
  reason_codes: ['LOW_MASTERY', 'HIGH_DECAY_RISK'],
  explanation_facts: {
    priority_mastery: 0.42,
    priority_decay_risk_score: 0.64
  },
  spaced_repetition: {
    generated_at: '2026-03-03T10:00:00Z',
    due_now_count: 1,
    due_next_24h_count: 2,
    review_queue: [
      {
        module_id: 'math',
        topic_id: 'Calculus',
        subtopic_id: 'Integration',
        interval_days: 1,
        due_in_days: -0.2,
        due_now: true,
        next_review_at: '2026-03-03T09:00:00Z',
        priority_score: 0.77
      },
      {
        module_id: 'math',
        topic_id: 'Probability',
        subtopic_id: 'Conditional Probability',
        interval_days: 2,
        due_in_days: 0.7,
        due_now: false,
        next_review_at: '2026-03-04T03:00:00Z',
        priority_score: 0.46
      }
    ]
  }
};

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function toPercent(value) {
  return Math.round(Number(value || 0) * 100);
}

function toRiskLabel(score) {
  if (score >= 0.5) return 'high';
  if (score >= 0.25) return 'medium';
  return 'low';
}

function summarizeTopics(state) {
  const grouped = {};
  for (const s of state.subtopics || []) {
    if (!grouped[s.topic_id]) {
      grouped[s.topic_id] = {
        name: s.topic_id,
        masteryTotal: 0,
        count: 0,
        maxRisk: 0
      };
    }
    grouped[s.topic_id].masteryTotal += Number(s.mastery || 0);
    grouped[s.topic_id].count += 1;
    grouped[s.topic_id].maxRisk = Math.max(grouped[s.topic_id].maxRisk, Number(s.decay_risk_score || 0));
  }
  return Object.values(grouped).map((topic) => ({
    name: topic.name,
    mastery: Math.round((topic.masteryTotal / Math.max(1, topic.count)) * 100),
    risk: toRiskLabel(topic.maxRisk)
  }));
}

function render(state, insight, spacedPlan, source) {
  const topics = summarizeTopics(state);
  const subtopics = state.subtopics || [];
  const repetition = spacedPlan || insight.spaced_repetition;

  nodes.xpValue.textContent = state.xp_total ?? '-';

  const masteredCount = topics.filter((t) => Number(t.mastery) >= 70).length;
  const riskCount = subtopics.filter((s) => Number(s.decay_risk_score) >= 0.5).length;

  nodes.masteredValue.textContent = masteredCount;
  nodes.riskValue.textContent = riskCount;

  nodes.masteryChart.innerHTML = topics
    .map(
      (topic) => `
      <div class="bar-item">
        <span class="bar-label">${topic.name}</span>
        <div class="bar-track">
          <div class="bar-fill" style="width:${Math.max(0, Math.min(100, Number(topic.mastery)))}%"></div>
        </div>
        <span class="bar-value">${topic.mastery}%</span>
      </div>
    `
    )
    .join('');

  const weakTopics = subtopics
    .filter((s) => Number(s.mastery) < 0.6 || Number(s.decay_risk_score) >= 0.5)
    .sort((a, b) => Number(a.mastery) - Number(b.mastery));
  nodes.weakTopicsList.innerHTML = weakTopics.length
    ? weakTopics
        .map(
          (s) =>
            `<li>${s.topic_id} / ${s.subtopic_id} - Mastery ${toPercent(s.mastery)}% (${toRiskLabel(s.decay_risk_score)} risk)</li>`
        )
        .join('')
    : '<li>No weak topics detected.</li>';

  nodes.recommendation.innerHTML = `
    <p><strong>${insight.recommended_action || 'No recommendation available.'}</strong></p>
    <p class="muted">${(insight.reason_codes || []).join(', ')}</p>
  `;

  if (repetition) {
    nodes.reviewMeta.textContent = `Due now: ${repetition.due_now_count} | Due in next 24h: ${repetition.due_next_24h_count}`;
    nodes.reviewQueueList.innerHTML = (repetition.review_queue || []).length
      ? repetition.review_queue
          .slice(0, 6)
          .map(
            (item) =>
              `<li>${item.topic_id} / ${item.subtopic_id} - ${item.due_now ? 'Due now' : `In ${item.due_in_days} days`} (interval ${item.interval_days}d)</li>`
          )
          .join('')
      : '<li>No review items yet.</li>';
  } else {
    nodes.reviewMeta.textContent = 'No spaced repetition plan available.';
    nodes.reviewQueueList.innerHTML = '<li>No review items yet.</li>';
  }

  nodes.sourceNote.textContent = source;
}

async function loadDashboard() {
  const studentId = nodes.studentId.value.trim() || 'student-001';

  try {
    const [state, insight] = await Promise.all([
      fetchJson(`${API_BASE}/students/${studentId}/state`),
      fetchJson(`${API_BASE}/students/${studentId}/insights`)
    ]);

    let spacedPlan = insight.spaced_repetition || null;
    try {
      spacedPlan = await fetchJson(`${API_BASE}/students/${studentId}/spaced-repetition`);
    } catch (err) {
      // Keep fallback to the embedded insights payload when dedicated endpoint is unavailable.
    }

    render(state, insight, spacedPlan, `Using backend data from ${API_BASE} for ${studentId}.`);
  } catch (err) {
    render(
      mockState,
      mockInsight,
      mockInsight.spaced_repetition,
      `Backend unavailable (${err.message}). Showing deterministic mock data.`
    );
  }
}

nodes.refreshBtn.addEventListener('click', loadDashboard);
nodes.studentId.addEventListener('keydown', (ev) => {
  if (ev.key === 'Enter') loadDashboard();
});

loadDashboard();
