const API_BASE_URL = window.localStorage.getItem('apiBase') || 'http://localhost:8000';

const STORAGE_KEYS = {
  users: 'dlh_users',
  session: 'dlh_session',
  calendarEvents: 'dlh_calendar_events'
};

const charts = {
  trend: null,
  donut: null,
  comparison: null
};

const calendarState = {
  visibleDate: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
  selectedDateKey: null
};

let calendarActionsBound = false;

const nodes = {
  entrySplash: document.getElementById('entrySplash'),
  dashboardApp: document.getElementById('dashboardApp'),
  logoutBtn: document.getElementById('logoutBtn'),
  lastUpdated: document.getElementById('lastUpdated'),
  statusChip: document.getElementById('statusChip'),
  xpValue: document.getElementById('xpValue'),
  masteredValue: document.getElementById('masteredValue'),
  riskValue: document.getElementById('riskValue'),
  masteryChart: document.getElementById('masteryChart'),
  weakTopicsList: document.getElementById('weakTopicsList'),
  sourceNote: document.getElementById('sourceNote'),
  recommendationCard: document.getElementById('recommendationCard'),
  recommendationText: document.getElementById('recommendationText'),
  recommendationEvidence: document.getElementById('recommendationEvidence'),
  whyList: document.getElementById('whyList'),
  startPracticeBtn: document.getElementById('startPracticeBtn'),
  practicePanel: document.getElementById('practicePanel'),
  youtubeQuery: document.getElementById('youtubeQuery'),
  youtubeSearchBtn: document.getElementById('youtubeSearchBtn'),
  statsTableBody: document.getElementById('statsTableBody'),
  masteryTrendChart: document.getElementById('masteryTrendChart'),
  riskDonutChart: document.getElementById('riskDonutChart'),
  topicComparisonChart: document.getElementById('topicComparisonChart'),
  streakCurrent: document.getElementById('streakCurrent'),
  streakLongest: document.getElementById('streakLongest'),
  focusPlan: document.getElementById('focusPlan'),
  profileName: document.getElementById('profileName'),
  profileStudentId: document.getElementById('profileStudentId'),
  profileEmail: document.getElementById('profileEmail'),
  profileDob: document.getElementById('profileDob'),
  profileStreak: document.getElementById('profileStreak'),
  profileStreakNote: document.getElementById('profileStreakNote'),
  profileUpdates: document.getElementById('profileUpdates'),
  pageTabs: Array.from(document.querySelectorAll('.page-tab')),
  tabPanels: Array.from(document.querySelectorAll('.tab-panel')),
  calendarMonthLabel: document.getElementById('calendarMonthLabel'),
  prevMonthBtn: document.getElementById('prevMonthBtn'),
  nextMonthBtn: document.getElementById('nextMonthBtn'),
  calendarGrid: document.getElementById('calendarGrid'),
  eventModal: document.getElementById('eventModal'),
  eventDateLabel: document.getElementById('eventDateLabel'),
  eventTitle: document.getElementById('eventTitle'),
  eventType: document.getElementById('eventType'),
  saveEventBtn: document.getElementById('saveEventBtn'),
  closeModalBtn: document.getElementById('closeModalBtn'),
  closeModalXBtn: document.getElementById('closeModalXBtn')
};

const mockState = {
  student_id: 'student-001',
  total_xp: 1240,
  topics: [
    { name: 'Algebra', mastery: 82, risk: 'low', lastActivityDays: 1 },
    { name: 'Geometry', mastery: 66, risk: 'medium', lastActivityDays: 3 },
    { name: 'Trigonometry identities', mastery: 39, risk: 'high', lastActivityDays: 8 },
    { name: 'Calculus limits', mastery: 48, risk: 'high', lastActivityDays: 5 }
  ]
};

const mockInsight = {
  recommendation: 'Prioritize 2 short practice sets on Trigonometry identities with easy-to-medium difficulty.',
  reason_codes: ['accuracy_drop', 'inactivity'],
  weak_subtopics: ['Trigonometry identities', 'Calculus limits']
};

const mockPlan = {
  roadmap: [
    'Warmup: quick recap of trigonometric identities',
    'Practice set 1: mixed trigonometry questions',
    'Practice set 2: application problems',
    'Review incorrect attempts and summarize mistakes'
  ]
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

function getCalendarEvents() {
  return JSON.parse(window.localStorage.getItem(STORAGE_KEYS.calendarEvents) || '{}');
}

function setCalendarEvents(events) {
  window.localStorage.setItem(STORAGE_KEYS.calendarEvents, JSON.stringify(events));
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

function wait(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function daysSince(dateValue) {
  if (!dateValue) return 0;
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) return 0;
  const diffMs = Date.now() - date.getTime();
  return Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));
}

function topicLabel(mastery) {
  if (mastery >= 70) return 'Mastered';
  if (mastery >= 50) return 'Developing';
  return 'At-risk';
}

function heuristicReasons(topic) {
  const reasons = [];
  if (topic.risk === 'high') reasons.push('High risk • low accuracy');
  if (topic.lastActivityDays >= 7) reasons.push(`Decay risk • inactive ${topic.lastActivityDays}d`);
  if (topic.mastery < 60 && topic.lastActivityDays < 7) reasons.push('Slow response time');
  if (!reasons.length) reasons.push('Developing consistency');
  return reasons.slice(0, 2);
}

function normalizeState(state) {
  if (Array.isArray(state?.topics)) {
    return {
      student_id: state.student_id || state.learner_id || 'unknown',
      total_xp: Number(state.total_xp ?? state.xp_total ?? 0),
      topics: state.topics.map((topic) => {
        const mastery = Math.max(0, Math.min(100, Number(topic.mastery || 0)));
        const risk = String(topic.risk || (mastery < 50 ? 'high' : mastery < 70 ? 'medium' : 'low')).toLowerCase();
        const lastActivityDays = Number(topic.lastActivityDays ?? topic.last_activity_days ?? 0);
        return {
          name: topic.name || topic.topic_id || 'unknown',
          mastery,
          risk,
          lastActivityDays,
          label: topicLabel(mastery),
          reasons: heuristicReasons({ mastery, risk, lastActivityDays })
        };
      })
    };
  }

  const subtopics = Array.isArray(state?.subtopics) ? state.subtopics : [];
  const topicMap = new Map();

  subtopics.forEach((entry) => {
    const key = entry.topic_id || entry.subtopic_id || 'unknown';
    const current = topicMap.get(key) || {
      name: key,
      masterySum: 0,
      count: 0,
      maxRisk: 0,
      lastInteractionAt: null
    };

    current.masterySum += Number(entry.mastery || 0);
    current.count += 1;
    current.maxRisk = Math.max(current.maxRisk, Number(entry.decay_risk_score || 0));

    const interaction = entry.last_interaction_at;
    if (interaction && (!current.lastInteractionAt || new Date(interaction) > new Date(current.lastInteractionAt))) {
      current.lastInteractionAt = interaction;
    }

    topicMap.set(key, current);
  });

  const topics = Array.from(topicMap.values()).map((item) => {
    const mastery = Math.round((item.masterySum / Math.max(1, item.count)) * 100);
    const risk = item.maxRisk >= 0.67 ? 'high' : item.maxRisk >= 0.34 ? 'medium' : 'low';
    const lastActivityDays = daysSince(item.lastInteractionAt);

    return {
      name: item.name,
      mastery,
      risk,
      lastActivityDays,
      label: topicLabel(mastery),
      reasons: heuristicReasons({ mastery, risk, lastActivityDays })
    };
  });

  return {
    student_id: state?.learner_id || 'unknown',
    total_xp: Number(state?.xp_total || 0),
    topics
  };
}

function normalizeInsight(insight) {
  return {
    recommendation: insight?.recommendation || insight?.recommended_action || 'No recommendation available.',
    reasonCodes: Array.isArray(insight?.reason_codes) ? insight.reason_codes : [],
    weakSubtopics: Array.isArray(insight?.weak_subtopics) ? insight.weak_subtopics : []
  };
}

function normalizePlan(plan, topWeakTopicName) {
  const items = Array.isArray(plan?.roadmap)
    ? plan.roadmap
    : Array.isArray(plan?.items)
      ? plan.items
      : [];

  if (items.length >= 3) return items.slice(0, 3);

  const topic = topWeakTopicName || 'core weak topic';
  return [
    `Warmup review: ${topic} fundamentals`,
    `2 practice sets: ${topic} mixed questions`,
    'Revisit mistakes and summarize key errors'
  ];
}

function computeSummary(state) {
  const topics = Array.isArray(state.topics) ? state.topics : [];
  const atRiskTopicsCount = topics.filter((t) => t.risk === 'high' || t.mastery < 60).length;
  const masteredTopicsCount = topics.filter((t) => t.mastery >= 70).length;
  const developingTopicsCount = topics.filter((t) => t.mastery >= 50 && t.mastery < 70).length;
  const lastActivityDays = topics.length ? Math.min(...topics.map((t) => Number(t.lastActivityDays || 0))) : 0;
  const weakTopics = topics.filter((t) => t.mastery < 60 || t.risk === 'high');

  return {
    topics,
    weakTopics,
    atRiskTopicsCount,
    masteredTopicsCount,
    developingTopicsCount,
    lastActivityDays
  };
}

function computeStatus(atRiskTopicsCount, lastActivityDays) {
  if (atRiskTopicsCount >= 2) return 'At risk';
  if (lastActivityDays >= 7) return 'Inactive';
  return 'On track';
}

function updateStatusChip(label) {
  nodes.statusChip.textContent = label;
  nodes.statusChip.classList.remove('status-track', 'status-risk', 'status-inactive');
  if (label === 'At risk') nodes.statusChip.classList.add('status-risk');
  else if (label === 'Inactive') nodes.statusChip.classList.add('status-inactive');
  else nodes.statusChip.classList.add('status-track');
}

function updateLastUpdated() {
  nodes.lastUpdated.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
}

function recommendationMeta(summary, insight) {
  const topWeak = summary.weakTopics.slice().sort((a, b) => a.mastery - b.mastery)[0];
  const bullets = [];

  if (topWeak) bullets.push(`${topWeak.name} at ${topWeak.mastery}% mastery (${topWeak.risk} risk).`);
  if (summary.lastActivityDays >= 7) bullets.push(`Inactivity signal: ${summary.lastActivityDays} days since recent activity.`);
  if (summary.atRiskTopicsCount >= 2) bullets.push(`${summary.atRiskTopicsCount} topics are currently at-risk.`);
  if (!bullets.length) bullets.push('Current performance is stable; this recommendation keeps momentum high.');

  const evidence = topWeak
    ? `${topWeak.name} ${topWeak.mastery}% • ${summary.atRiskTopicsCount} at-risk topics • ${summary.lastActivityDays}d inactivity`
    : `No weak topics detected • ${summary.lastActivityDays}d inactivity`;

  return { topWeakTopic: topWeak, bullets: bullets.slice(0, 3), evidence };
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
  nodes.profileStreakNote.textContent = 'Maintain daily practice above 15 minutes to keep streak growth stable.';

  nodes.profileUpdates.innerHTML = [
    `Welcome ${user.name || 'Learner'}.`,
    `Student identity: ${user.studentId || 'new_student_001'}.`,
    'Calendar tab now supports personal planning events.'
  ]
    .map((item) => `<li>${item}</li>`)
    .join('');
}

function renderStatisticsTable(summary) {
  if (!summary.topics.length) {
    nodes.statsTableBody.innerHTML = '<tr><td colspan="4" class="muted">No topic data yet.</td></tr>';
    return;
  }

  nodes.statsTableBody.innerHTML = summary.topics
    .map(
      (topic) => `
      <tr>
        <td>${topic.name}</td>
        <td>${topic.mastery}% (${topic.label})</td>
        <td>${topic.lastActivityDays}d ago</td>
        <td>${topic.risk}</td>
      </tr>
    `
    )
    .join('');
}

function animateMasteryBars() {
  const fills = nodes.masteryChart.querySelectorAll('.bar-fill');
  fills.forEach((fill) => {
    const target = fill.dataset.width || '0';
    fill.style.width = '0%';
    window.requestAnimationFrame(() => {
      fill.style.width = `${target}%`;
    });
  });
}

function renderStudyStreak(summary, user) {
  const current = Math.max(1, computeDemoStreak(user.studentId) - Math.min(2, summary.lastActivityDays));
  const longest = current + 6;
  nodes.streakCurrent.textContent = `${current} days`;
  nodes.streakLongest.textContent = `Longest streak: ${longest} days`;
}

function renderFocusPlan(planItems) {
  nodes.focusPlan.innerHTML = planItems
    .map(
      (item, idx) => `
      <label>
        <input type="checkbox" id="focus-${idx}" />
        <span>${item}</span>
      </label>
    `
    )
    .join('');
}

function destroyChart(instance) {
  if (instance && typeof instance.destroy === 'function') instance.destroy();
}

function last7DateLabels() {
  const labels = [];
  for (let i = 6; i >= 0; i -= 1) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    labels.push(date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }));
  }
  return labels;
}

function trendSeriesForTopic(topicName, mastery) {
  const seed = Array.from(topicName).reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  return Array.from({ length: 7 }, (_, idx) => {
    const drift = (idx - 3) * 1.2;
    const wobble = ((seed + idx * 17) % 5) - 2;
    const value = mastery - 5 + drift + wobble;
    return Math.max(15, Math.min(99, Math.round(value)));
  });
}

function renderCharts(summary) {
  if (typeof window.Chart === 'undefined') return;

  const labels = last7DateLabels();
  const colorMap = {
    'Algebra': '#007a78',
    'Geometry': '#22a19f',
    'Trigonometry identities': '#48b5a7',
    'Calculus limits': '#7bc8b6'
  };

  const orderedTopics = ['Algebra', 'Geometry', 'Trigonometry identities', 'Calculus limits'];
  const datasets = orderedTopics
    .map((name) => {
      const topic = summary.topics.find((t) => t.name === name) || { mastery: 55 };
      return {
        label: name,
        data: trendSeriesForTopic(name, topic.mastery),
        borderColor: colorMap[name],
        backgroundColor: 'transparent',
        pointRadius: 2,
        tension: 0.35,
        borderWidth: 2
      };
    });

  destroyChart(charts.trend);
  charts.trend = new window.Chart(nodes.masteryTrendChart, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.dataset.label} • ${context.label}: ${context.parsed.y}%`;
            }
          }
        }
      },
      scales: {
        y: { min: 0, max: 100, grid: { color: '#eef1e8' } },
        x: { grid: { display: false } }
      }
    }
  });

  destroyChart(charts.donut);
  charts.donut = new window.Chart(nodes.riskDonutChart, {
    type: 'doughnut',
    data: {
      labels: ['Mastered', 'Developing', 'At-risk'],
      datasets: [
        {
          data: [summary.masteredTopicsCount, summary.developingTopicsCount, summary.atRiskTopicsCount],
          backgroundColor: ['#2a9d8f', '#e9b44c', '#b3261e']
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 10 } }
      }
    }
  });

  destroyChart(charts.comparison);
  charts.comparison = new window.Chart(nodes.topicComparisonChart, {
    type: 'bar',
    data: {
      labels: summary.topics.map((t) => t.name),
      datasets: [
        {
          data: summary.topics.map((t) => t.mastery),
          backgroundColor: summary.topics.map((t) =>
            t.label === 'Mastered' ? '#2a9d8f' : t.label === 'Developing' ? '#e9b44c' : '#b3261e'
          )
        }
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { min: 0, max: 100, grid: { color: '#eef1e8' } },
        y: { grid: { display: false } }
      }
    }
  });
}

function wireWeakTopicClicks(summary) {
  const items = nodes.weakTopicsList.querySelectorAll('li.clickable');
  items.forEach((item) => {
    item.addEventListener('click', () => {
      items.forEach((it) => it.classList.remove('active'));
      item.classList.add('active');
      const topicName = item.dataset.topic || summary.weakTopics[0]?.name || 'study skills';
      nodes.youtubeQuery.value = topicName;
      nodes.recommendationCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });
}

function formatDateKey(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function tagClassForType(type) {
  if (type === 'Exam') return 'tag-exam';
  if (type === 'Assignment') return 'tag-assignment';
  if (type === 'Revision') return 'tag-revision';
  return 'tag-custom';
}

function renderCalendar() {
  const year = calendarState.visibleDate.getFullYear();
  const month = calendarState.visibleDate.getMonth();
  nodes.calendarMonthLabel.textContent = calendarState.visibleDate.toLocaleDateString(undefined, {
    month: 'long',
    year: 'numeric'
  });

  const firstDay = new Date(year, month, 1);
  const startOffset = (firstDay.getDay() + 6) % 7;
  const startDate = new Date(year, month, 1 - startOffset);
  const events = getCalendarEvents();
  const todayKey = formatDateKey(new Date());

  const cells = [];
  for (let i = 0; i < 42; i += 1) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    const key = formatDateKey(date);
    const dayEvents = Array.isArray(events[key]) ? events[key] : [];
    const otherMonth = date.getMonth() !== month;
    const today = key === todayKey;

    cells.push(`
      <button class="calendar-day ${otherMonth ? 'other-month' : ''} ${today ? 'today' : ''}" data-date="${key}" type="button">
        <span class="day-num">${date.getDate()}</span>
        ${dayEvents
          .slice(0, 2)
          .map((evt) => `<span class="event-tag ${tagClassForType(evt.type)}">${evt.title}</span>`)
          .join('')}
      </button>
    `);
  }

  nodes.calendarGrid.innerHTML = cells.join('');
  nodes.calendarGrid.querySelectorAll('.calendar-day').forEach((button) => {
    button.addEventListener('click', () => openEventModal(button.dataset.date));
  });
}

function openEventModal(dateKey) {
  calendarState.selectedDateKey = dateKey;
  nodes.eventDateLabel.textContent = `Date: ${dateKey}`;
  nodes.eventTitle.value = '';
  nodes.eventType.value = 'Exam';
  nodes.eventModal.classList.remove('hidden');
  document.body.classList.add('modal-open');
}

function closeEventModal() {
  nodes.eventModal.classList.add('hidden');
  document.body.classList.remove('modal-open');
}

function saveCalendarEvent() {
  const title = (nodes.eventTitle.value || '').trim();
  const type = nodes.eventType.value;
  const dateKey = calendarState.selectedDateKey;
  if (!title || !dateKey) return;

  const events = getCalendarEvents();
  const existing = Array.isArray(events[dateKey]) ? events[dateKey] : [];
  existing.push({ title, type });
  events[dateKey] = existing;
  setCalendarEvents(events);

  closeEventModal();
  renderCalendar();
}

function setupCalendarActions() {
  if (calendarActionsBound) return;
  calendarActionsBound = true;

  nodes.prevMonthBtn.addEventListener('click', () => {
    calendarState.visibleDate = new Date(calendarState.visibleDate.getFullYear(), calendarState.visibleDate.getMonth() - 1, 1);
    renderCalendar();
  });

  nodes.nextMonthBtn.addEventListener('click', () => {
    calendarState.visibleDate = new Date(calendarState.visibleDate.getFullYear(), calendarState.visibleDate.getMonth() + 1, 1);
    renderCalendar();
  });

  nodes.closeModalBtn.addEventListener('click', closeEventModal);
  nodes.closeModalXBtn.addEventListener('click', closeEventModal);
  nodes.saveEventBtn.addEventListener('click', saveCalendarEvent);

  nodes.eventModal.addEventListener('click', (event) => {
    if (event.target === nodes.eventModal) closeEventModal();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeEventModal();
  });
}

function initializeModalState() {
  closeEventModal();
}

function render(state, insight, planItems, source, user) {
  const summary = computeSummary(state);
  const status = computeStatus(summary.atRiskTopicsCount, summary.lastActivityDays);
  const recMeta = recommendationMeta(summary, insight);

  nodes.xpValue.textContent = state.total_xp ?? '-';
  nodes.masteredValue.textContent = summary.masteredTopicsCount;
  nodes.riskValue.textContent = summary.atRiskTopicsCount;
  updateStatusChip(status);

  nodes.masteryChart.innerHTML = summary.topics
    .map(
      (topic) => `
      <div class="bar-item">
        <span class="bar-label">${topic.name}</span>
        <div class="bar-track" title="Mastery: ${topic.mastery}% • Last activity: ${topic.lastActivityDays}d • ${topic.reasons.join(' • ')}">
          <div class="bar-fill" data-width="${Math.max(0, Math.min(100, Number(topic.mastery)))}"></div>
          <span class="bar-threshold">70%</span>
        </div>
        <span class="bar-value">${topic.mastery}%</span>
        <span class="bar-status">${topic.label}</span>
      </div>
    `
    )
    .join('');

  animateMasteryBars();

  nodes.weakTopicsList.innerHTML = summary.weakTopics.length
    ? summary.weakTopics
        .map(
          (topic) => `<li class="clickable" data-topic="${topic.name}">${topic.name} - Mastery ${topic.mastery}% <span class="reason-tag">${topic.reasons.join(' • ')}</span></li>`
        )
        .join('')
    : '<li>No weak topics detected.</li>';

  wireWeakTopicClicks(summary);

  nodes.recommendationText.innerHTML = `<strong>${insight.recommendation}</strong>`;
  nodes.recommendationEvidence.textContent = `Evidence: ${recMeta.evidence}`;
  nodes.whyList.innerHTML = recMeta.bullets.map((bullet) => `<li>${bullet}</li>`).join('');

  const ytTopic = recMeta.topWeakTopic?.name || insight.weakSubtopics[0] || summary.topics[0]?.name || 'study skills';
  nodes.youtubeQuery.value = ytTopic;

  renderStatisticsTable(summary);
  renderStudyStreak(summary, user);
  renderFocusPlan(planItems);
  renderCharts(summary);

  nodes.sourceNote.textContent = source;
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function loadDashboard(studentId, user) {
  const safeStudentId = studentId || 'student-001';

  try {
    const [rawState, rawInsight, rawPlan] = await Promise.all([
      fetchJson(`${API_BASE_URL}/students/${safeStudentId}/state`),
      fetchJson(`${API_BASE_URL}/students/${safeStudentId}/insights`),
      fetchJson(`${API_BASE_URL}/students/${safeStudentId}/plan?days=7`)
    ]);

    const state = normalizeState(rawState);
    const insight = normalizeInsight(rawInsight);
    const summary = computeSummary(state);
    const topWeak = summary.weakTopics[0]?.name;
    const planItems = normalizePlan(rawPlan, topWeak);
    render(state, insight, planItems, `Using backend data from ${API_BASE_URL} for ${safeStudentId}.`, user);
    updateLastUpdated();
  } catch (err) {
    const state = normalizeState(mockState);
    const insight = normalizeInsight(mockInsight);
    const summary = computeSummary(state);
    const topWeak = summary.weakTopics[0]?.name;
    const planItems = normalizePlan(mockPlan, topWeak);
    render(state, insight, planItems, `Backend unavailable (${err.message}). Showing deterministic mock data.`, user);
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

function setupRecommendationActions(user) {
  nodes.startPracticeBtn.addEventListener('click', () => {
    nodes.practicePanel.classList.toggle('hidden');
  });

  nodes.youtubeSearchBtn.addEventListener('click', () => {
    const query = encodeURIComponent((nodes.youtubeQuery.value || '').trim() || `${user.studentId} practice`);
    window.open(`https://www.youtube.com/results?search_query=${query}`, '_blank', 'noopener');
  });
}

function setupTabs() {
  nodes.pageTabs.forEach((button) => {
    button.addEventListener('click', () => {
      const tab = button.dataset.tab;
      switchTab(tab);
      if (tab === 'calendar') renderCalendar();
    });
  });
}

function switchTab(tabKey) {
  nodes.pageTabs.forEach((button) => {
    button.classList.toggle('active', button.dataset.tab === tabKey);
  });

  nodes.tabPanels.forEach((panel) => {
    panel.classList.toggle('hidden', panel.dataset.panel !== tabKey);
  });
}

nodes.logoutBtn.addEventListener('click', () => {
  clearSession();
  window.location.href = 'login.html';
});

const user = authGuard();
if (user) {
  initializeModalState();
  updateLastUpdated();
  setupTabs();
  switchTab('dashboard');
  renderProfile(user);
  setupRecommendationActions(user);
  setupCalendarActions();
  renderCalendar();
  revealDashboard();
  loadDashboard(user.studentId, user);
}

document.addEventListener('DOMContentLoaded', () => {
  initializeModalState();
});
