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

function setSession(email) {
  window.localStorage.setItem(STORAGE_KEYS.session, JSON.stringify({ email }));
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
  if (nodes.loginForm) nodes.loginForm.classList.add('hidden');
  if (nodes.registerForm) nodes.registerForm.classList.add('hidden');
  if (nodes.verifyForm) nodes.verifyForm.classList.remove('hidden');

  if (nodes.verifyHint) {
    nodes.verifyHint.textContent = `Verification sent for ${email}.`;
  }

  if (nodes.verifyMode) {
    if (mode === 'real') {
      nodes.verifyMode.textContent = 'Email sent via backend verification service.';
    } else {
      nodes.verifyMode.textContent = `Demo mode active: use code ${code}.`;
    }
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

    const newUser = { name, email, dob, password, verified: false, verificationCode: '' };
    users.push(newUser);
    saveUsers(users);

    await beginVerification(newUser);
  });
}

if (nodes.loginForm) {
  nodes.loginForm.addEventListener('submit', async (ev) => {
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
      await beginVerification(user);
      return;
    }

    setSession(user.email);
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
      if (pageMode === 'login') {
        window.location.href = 'register.html';
      }
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

    setSession(user.email);
    redirectToDashboard();
  });
}

bootGuard();
