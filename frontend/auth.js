const API_BASE = window.localStorage.getItem('apiBase') || 'http://localhost:8000';

const STORAGE_KEYS = {
  users: 'dlh_users',
  session: 'dlh_session',
  pendingVerify: 'dlh_pending_verify'
};

const pageMode = document.body.dataset.authPage;

const nodes = {
  authMessage: document.getElementById('authMessage'),
  loginForm: document.getElementById('loginForm'),
  registerForm: document.getElementById('registerForm'),
  verifyForm: document.getElementById('verifyForm'),
  verifyHint: document.getElementById('verifyHint'),
  verifyMode: document.getElementById('verifyMode')
};

function getUsers() {
  return JSON.parse(window.localStorage.getItem(STORAGE_KEYS.users) || '[]');
}

function saveUsers(users) {
  window.localStorage.setItem(STORAGE_KEYS.users, JSON.stringify(users));
}

function setSession(user) {
  window.localStorage.setItem(
    STORAGE_KEYS.session,
    JSON.stringify({ email: user.email, studentId: user.studentId })
  );
}

function getCurrentSession() {
  return JSON.parse(window.localStorage.getItem(STORAGE_KEYS.session) || 'null');
}

function setMessage(text, type = 'ok') {
  if (!nodes.authMessage) return;
  nodes.authMessage.textContent = text;
  nodes.authMessage.className = `status-msg ${type === 'error' ? 'error' : 'ok'}`;
}

function generateCode() {
  return String(Math.floor(100000 + Math.random() * 900000));
}

function getNextStudentId(users) {
  const maxSeen = users.reduce((max, user) => {
    const match = String(user.studentId || '').match(/^new_student_(\d+)$/);
    if (!match) return max;
    return Math.max(max, Number(match[1]));
  }, 0);

  const nextNumber = String(maxSeen + 1).padStart(3, '0');
  return `new_student_${nextNumber}`;
}

async function sendVerificationEmail(email, code) {
  try {
    const res = await fetch(`${API_BASE}/auth/send-verification`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return { mode: 'real' };
  } catch {
    return { mode: 'demo' };
  }
}

function showVerifyForm(email, code, mode) {
  if (nodes.registerForm) nodes.registerForm.classList.add('hidden');
  if (nodes.verifyForm) nodes.verifyForm.classList.remove('hidden');

  if (nodes.verifyHint) {
    nodes.verifyHint.textContent = `Verification sent for ${email}.`;
  }

  if (nodes.verifyMode) {
    nodes.verifyMode.textContent =
      mode === 'real'
        ? 'Email sent via backend verification service.'
        : `Demo mode active: use code ${code}.`;
  }

  setMessage('Enter the verification code to continue.', 'ok');
}

async function beginVerification(user) {
  const verificationCode = user.verificationCode || generateCode();
  user.verificationCode = verificationCode;

  const users = getUsers();
  const idx = users.findIndex((item) => item.email === user.email);
  if (idx !== -1) {
    users[idx] = user;
    saveUsers(users);
  }

  window.localStorage.setItem(STORAGE_KEYS.pendingVerify, user.email);
  const delivery = await sendVerificationEmail(user.email, verificationCode);
  showVerifyForm(user.email, verificationCode, delivery.mode);
}

function redirectToDashboard() {
  window.location.href = 'index.html';
}

function bootGuard() {
  const session = getCurrentSession();
  if (!session?.email) return;

  const user = getUsers().find((item) => item.email === session.email && item.verified);
  if (user) redirectToDashboard();
}

if (nodes.registerForm) {
  nodes.registerForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();

    const name = document.getElementById('registerName').value.trim();
    const email = document.getElementById('registerEmail').value.trim().toLowerCase();
    const dob = document.getElementById('registerDob').value;
    const password = document.getElementById('registerPassword').value;

    const users = getUsers();
    const exists = users.find((user) => user.email === email);
    if (exists) {
      setMessage('This email is already registered. Please login instead.', 'error');
      return;
    }

    const newUser = {
      name,
      email,
      dob,
      password,
      studentId: getNextStudentId(users),
      verified: false,
      verificationCode: ''
    };

    users.push(newUser);
    saveUsers(users);

    await beginVerification(newUser);
  });
}

if (nodes.loginForm) {
  nodes.loginForm.addEventListener('submit', (ev) => {
    ev.preventDefault();

    const email = document.getElementById('loginEmail').value.trim().toLowerCase();
    const password = document.getElementById('loginPassword').value;

    const users = getUsers();
    const user = users.find((item) => item.email === email && item.password === password);

    if (!user) {
      setMessage('Invalid email or password.', 'error');
      return;
    }

    if (!user.verified) {
      setMessage('Please verify this account from Register page first.', 'error');
      return;
    }

    setSession(user);
    redirectToDashboard();
  });
}

if (nodes.verifyForm) {
  nodes.verifyForm.addEventListener('submit', (ev) => {
    ev.preventDefault();

    const email = window.localStorage.getItem(STORAGE_KEYS.pendingVerify);
    const enteredCode = document.getElementById('verificationCode').value.trim();

    if (!email) {
      setMessage('No pending verification. Please register again.', 'error');
      return;
    }

    const users = getUsers();
    const user = users.find((item) => item.email === email);

    if (!user || user.verificationCode !== enteredCode) {
      setMessage('Invalid verification code. Try again.', 'error');
      return;
    }

    user.verified = true;
    user.verificationCode = '';
    saveUsers(users);
    window.localStorage.removeItem(STORAGE_KEYS.pendingVerify);

    setSession(user);
    redirectToDashboard();
  });
}

if (pageMode === 'register' && window.localStorage.getItem(STORAGE_KEYS.pendingVerify)) {
  const email = window.localStorage.getItem(STORAGE_KEYS.pendingVerify);
  const user = getUsers().find((item) => item.email === email && !item.verified);
  if (user && nodes.registerForm) {
    nodes.registerForm.classList.add('hidden');
    nodes.verifyForm.classList.remove('hidden');
    nodes.verifyHint.textContent = `Complete verification for ${user.email}.`;
    nodes.verifyMode.textContent = user.verificationCode
      ? `Demo mode active: use code ${user.verificationCode}.`
      : '';
  }
}

bootGuard();
