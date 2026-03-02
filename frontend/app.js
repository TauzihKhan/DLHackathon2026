const API_BASE = window.localStorage.getItem('apiBase') || 'http://localhost:8000';

const STORAGE_KEYS = {
  users: 'dlh_users',
  session: 'dlh_session'
};

const nodes = {
  logoutBtn: document.getElementById('logoutBtn'),
  studentId: document.getElementById('studentId'),
  refreshBtn: document.getElementById('refreshBtn'),
  xpValue: document.getElementById('xpValue'),
  masteredValue: document.getElementById('masteredValue'),
  riskValue: document.getElementById('riskValue'),
  masteryChart: document.getElementById('masteryChart'),
  weakTopicsList: document.getElementById('weakTopicsList'),
  recommendation: document.getElementById('recommendation'),
  sourceNote: document.getElementById('sourceNote')
};

const mockState = {
  student_id: 'student-001',
  total_xp: 1240,
  topics: [
    { name: 'Algebra', mastery: 82, risk: 'low' },
    { name: 'Geometry', mastery: 66, risk: 'medium' },
    { name: 'Trigonometry', mastery: 39, risk: 'high' },
    { name: 'Calculus', mastery: 48, risk: 'high' }
  ]
};

const mockInsight = {
  recommendation: 'Prioritize 2 short practice sets on Trigonometry identities with easy-to-medium difficulty.',
  explanation: 'Accuracy dropped to 40% over the last two sessions and response time is increasing.'
};

function getUsers() {
  return JSON.parse(window.localStorage.getItem(STORAGE_KEYS.users) || '[]');
}

function getCurrentSession() {
  return JSON.parse(window.localStorage.getItem(STORAGE_KEYS.session) || 'null');
}

function clearSession() {
  window.localStorage.removeItem(STORAGE_KEYS.session);
}

function authGuard() {
  const session = getCurrentSession();
  if (!session?.email) {
    window.location.href = 'login.html';
    return false;
  }

  const user = getUsers().find((item) => item.email === session.email && item.verified);
  if (!user) {
    clearSession();
    window.location.href = 'login.html';
    return false;
  }

  return true;
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function render(state, insight, source) {
  nodes.xpValue.textContent = state.total_xp ?? '-';

  const masteredCount = state.topics.filter((t) => Number(t.mastery) >= 70).length;
  const riskCount = state.topics.filter((t) => String(t.risk).toLowerCase() === 'high').length;

  nodes.masteredValue.textContent = masteredCount;
  nodes.riskValue.textContent = riskCount;

  nodes.masteryChart.innerHTML = state.topics
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

  const weakTopics = state.topics.filter((t) => Number(t.mastery) < 60 || String(t.risk).toLowerCase() === 'high');
  nodes.weakTopicsList.innerHTML = weakTopics.length
    ? weakTopics.map((t) => `<li>${t.name} - Mastery ${t.mastery}% (${t.risk} risk)</li>`).join('')
    : '<li>No weak topics detected.</li>';

  nodes.recommendation.innerHTML = `
    <p><strong>${insight.recommendation || 'No recommendation available.'}</strong></p>
    <p class="muted">${insight.explanation || ''}</p>
  `;

  nodes.sourceNote.textContent = source;
}

async function loadDashboard() {
  const studentId = nodes.studentId.value.trim() || 'student-001';

  try {
    const [state, insight] = await Promise.all([
      fetchJson(`${API_BASE}/students/${studentId}/state`),
      fetchJson(`${API_BASE}/students/${studentId}/insights`)
    ]);
    render(state, insight, `Using backend data from ${API_BASE} for ${studentId}.`);
  } catch (err) {
    render(mockState, mockInsight, `Backend unavailable (${err.message}). Showing deterministic mock data.`);
  }
}

nodes.logoutBtn.addEventListener('click', () => {
  clearSession();
  window.location.href = 'login.html';
});

nodes.refreshBtn.addEventListener('click', loadDashboard);
nodes.studentId.addEventListener('keydown', (ev) => {
  if (ev.key === 'Enter') loadDashboard();
});

if (authGuard()) {
  loadDashboard();
}
