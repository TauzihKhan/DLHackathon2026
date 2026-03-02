const API_BASE = window.localStorage.getItem('apiBase') || 'http://localhost:8000';

const STORAGE_KEYS = {
  users: 'dlh_users',
  session: 'dlh_session'
};

const nodes = {
  entrySplash: document.getElementById('entrySplash'),
  dashboardApp: document.getElementById('dashboardApp'),
  logoutBtn: document.getElementById('logoutBtn'),
  refreshBtn: document.getElementById('refreshBtn'),
  xpValue: document.getElementById('xpValue'),
  masteredValue: document.getElementById('masteredValue'),
  riskValue: document.getElementById('riskValue'),
  masteryChart: document.getElementById('masteryChart'),
  weakTopicsList: document.getElementById('weakTopicsList'),
  recommendation: document.getElementById('recommendation'),
  sourceNote: document.getElementById('sourceNote'),
  profileName: document.getElementById('profileName'),
  profileStudentId: document.getElementById('profileStudentId'),
  profileEmail: document.getElementById('profileEmail'),
  profileDob: document.getElementById('profileDob'),
  profileStreak: document.getElementById('profileStreak'),
  profileStreakNote: document.getElementById('profileStreakNote'),
  profileUpdates: document.getElementById('profileUpdates'),
  pageTabs: Array.from(document.querySelectorAll('.page-tab')),
  tabPanels: Array.from(document.querySelectorAll('.tab-panel'))
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

function normalizeState(state) {
  if (Array.isArray(state?.topics)) {
    return state;
  }

  const subtopics = Array.isArray(state?.subtopics) ? state.subtopics : [];
  const topicMap = new Map();

  subtopics.forEach((entry) => {
    const key = entry.topic_id || entry.subtopic_id || 'unknown';
    const current = topicMap.get(key) || { name: key, masterySum: 0, count: 0, maxRisk: 0 };
    current.masterySum += Number(entry.mastery || 0);
    current.count += 1;
    current.maxRisk = Math.max(current.maxRisk, Number(entry.decay_risk_score || 0));
    topicMap.set(key, current);
  });

  const topics = Array.from(topicMap.values()).map((item) => {
    const mastery = Math.round((item.masterySum / Math.max(1, item.count)) * 100);
    const risk =
      item.maxRisk >= 0.67 ? 'high' : item.maxRisk >= 0.34 ? 'medium' : 'low';
    return { name: item.name, mastery, risk };
  });

  return {
    student_id: state?.learner_id || 'unknown',
    total_xp: Number(state?.xp_total || 0),
    topics
  };
}

function normalizeInsight(insight) {
  if (insight?.recommendation || insight?.explanation) {
    return insight;
  }

  const weak = Array.isArray(insight?.weak_subtopics) ? insight.weak_subtopics : [];
  const reasonCodes = Array.isArray(insight?.reason_codes) ? insight.reason_codes.join(', ') : '';

  return {
    recommendation: insight?.recommended_action || 'No recommendation available.',
    explanation:
      weak.length || reasonCodes
        ? `Weak areas: ${weak.join(', ') || 'none'}. Reason codes: ${reasonCodes || 'none'}.`
        : 'No explanation facts returned yet.'
  };
}

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
    return null;
  }

  const user = getUsers().find((item) => item.email === session.email && item.verified);
  if (!user) {
    clearSession();
    window.location.href = 'login.html';
    return null;
  }

  return user;
}

function switchTab(tabKey) {
  nodes.pageTabs.forEach((button) => {
    button.classList.toggle('active', button.dataset.tab === tabKey);
  });

  nodes.tabPanels.forEach((panel) => {
    panel.classList.toggle('hidden', panel.dataset.panel !== tabKey);
  });
}

function setupTabs() {
  nodes.pageTabs.forEach((button) => {
    button.addEventListener('click', () => switchTab(button.dataset.tab));
  });
}

function wait(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function computeDemoStreak(studentId = '') {
  const numeric = Array.from(studentId).reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  return 3 + (numeric % 11);
}

function renderProfile(user) {
  const streak = computeDemoStreak(user.studentId);
  nodes.profileName.textContent = user.name || 'Learner';
  nodes.profileStudentId.textContent = user.studentId || 'new_student_001';
  nodes.profileEmail.textContent = user.email || '-';
  nodes.profileDob.textContent = user.dob || '-';
  nodes.profileStreak.textContent = `${streak} days`;
  nodes.profileStreakNote.textContent = 'Keep daily practice sessions above 15 minutes to maintain streak momentum.';

  nodes.profileUpdates.innerHTML = [
    `Welcome, ${user.name || 'Learner'} - your account is active.`,
    `Student identity assigned: ${user.studentId || 'new_student_001'}.`,
    'Dashboard metrics update from learner-state engine endpoints.',
    'New tabs (Statistics, Assignments, Tests & Scores) are ready for backend data wiring.'
  ]
    .map((item) => `<li>${item}</li>`)
    .join('');
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

async function loadDashboard(studentId) {
  const safeStudentId = studentId || 'student-001';

  try {
    const [rawState, rawInsight] = await Promise.all([
      fetchJson(`${API_BASE}/students/${safeStudentId}/state`),
      fetchJson(`${API_BASE}/students/${safeStudentId}/insights`)
    ]);
    const state = normalizeState(rawState);
    const insight = normalizeInsight(rawInsight);
    render(state, insight, `Using backend data from ${API_BASE} for ${safeStudentId}.`);
  } catch (err) {
    render(mockState, mockInsight, `Backend unavailable (${err.message}). Showing deterministic mock data.`);
  }
}

async function revealDashboard() {
  await wait(750);
  nodes.dashboardApp.classList.remove('dashboard-hidden');
  nodes.dashboardApp.classList.add('dashboard-visible');

  if (nodes.entrySplash) {
    nodes.entrySplash.classList.add('splash-exit');
    window.setTimeout(() => {
      nodes.entrySplash.remove();
    }, 420);
  }
}

nodes.logoutBtn.addEventListener('click', () => {
  clearSession();
  window.location.href = 'login.html';
});

const user = authGuard();
if (user) {
  setupTabs();
  switchTab('dashboard');
  renderProfile(user);

  nodes.refreshBtn.addEventListener('click', () => {
    loadDashboard(user.studentId);
  });

  revealDashboard();
  loadDashboard(user.studentId);
}
