const API_BASE = "http://localhost:5000/api";
let contextInterval = null;

// Select DOM Elements
const authSection = document.getElementById('auth-section');
const dashboardSection = document.getElementById('dashboard-section');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const usernameGroup = document.getElementById('username-group');
const usernameInput = document.getElementById('username');
const loginBtn = document.getElementById('login-btn');
const toggleRegisterBtn = document.getElementById('toggle-register-btn');
const authMessage = document.getElementById('auth-message');
const welcomeMsg = document.getElementById('welcome-msg');
const logoutBtn = document.getElementById('logout-btn');

const goalInput = document.getElementById('goal-input');
const startSessionBtn = document.getElementById('start-session-btn');
const stopSessionBtn = document.getElementById('stop-session-btn');
const pingBtn = document.getElementById('ping-btn');
const sessionMessage = document.getElementById('session-message');
const aiSuggestionBox = document.getElementById('ai-suggestion-box');

let isRegisterMode = false;

function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        authSection.classList.add('hidden');
        dashboardSection.classList.remove('hidden');
        welcomeMsg.innerText = `Welcome, ${localStorage.getItem('username')}`;
        fetchContextStatus(); 
    } else {
        authSection.classList.remove('hidden');
        dashboardSection.classList.add('hidden');
        stopContextEngine();
    }
}

// UI Toggles
toggleRegisterBtn.addEventListener('click', () => {
    isRegisterMode = !isRegisterMode;
    if (isRegisterMode) {
        usernameGroup.style.display = 'block';
        loginBtn.innerText = 'Create Account';
        toggleRegisterBtn.innerText = 'Already have an account? Login';
    } else {
        usernameGroup.style.display = 'none';
        loginBtn.innerText = 'Login';
        toggleRegisterBtn.innerText = 'Need to Register?';
    }
    authMessage.innerText = "";
});

// Auth Logic
loginBtn.addEventListener('click', async () => {
    const email = emailInput.value;
    const password = passwordInput.value;
    if (isRegisterMode) {
        const username = usernameInput.value;
        try {
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, email, password})
            });
            const data = await res.json();
            if (res.ok) {
                authMessage.style.color = "var(--success)";
                authMessage.innerText = "Registration successful! You may now login.";
                toggleRegisterBtn.click();
            } else {
                authMessage.style.color = "var(--danger)";
                authMessage.innerText = data.error || "Registration failed.";
            }
        } catch (err) { authMessage.innerText = "Error connecting to backend."; }
    } else {
        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            const data = await res.json();
            if (res.ok) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('username', data.username);
                checkAuth();
            } else {
                authMessage.style.color = "var(--danger)";
                authMessage.innerText = data.error || "Login failed.";
            }
        } catch (err) { authMessage.innerText = "Error connecting to backend."; }
    }
});

logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    checkAuth();
});

// Phase 8: Ping Logic
pingBtn.addEventListener('click', async () => {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_BASE}/sessions/ping`, {
            method: 'POST',
            headers: {'Authorization': `Bearer ${token}`}
        });
        if (res.ok) {
            pingBtn.classList.add('hidden');
            aiSuggestionBox.innerHTML = "<p>Activity confirmed! Keep going 🚀</p>";
            sessionMessage.innerText = "Session Active 🟢";
        }
    } catch (e) {}
});

// Start & Stop Logic
async function performSessionAction(action) {
    const token = localStorage.getItem('token');
    const endpoint = action === 'start' ? '/sessions/start' : '/sessions/stop';
    const body = action === 'start' ? { goal: goalInput.value } : {};

    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        
        if (res.ok) {
            if (action === 'start') {
                startSessionBtn.classList.add('hidden');
                stopSessionBtn.classList.remove('hidden');
                pingBtn.classList.add('hidden');
                sessionMessage.innerText = "Session Active 🟢";
                startContextEngine(); 
            } else {
                startSessionBtn.classList.remove('hidden');
                stopSessionBtn.classList.add('hidden');
                pingBtn.classList.add('hidden');
                sessionMessage.innerText = `Session Completed. Duration: ${data.duration_minutes} mins 🔴`;
                stopContextEngine();
                aiSuggestionBox.innerHTML = "<p>Session ended. Good job!</p>";
            }
        } else {
            sessionMessage.innerText = data.error || "Failed to process session";
            if (data.error && data.error.includes("already have an active")) {
                startSessionBtn.classList.add('hidden');
                stopSessionBtn.classList.remove('hidden');
                sessionMessage.innerText = "Session Active 🟢";
                startContextEngine();
            }
        }
    } catch (err) {
        sessionMessage.innerText = "Server error communicating with backend.";
    }
}

startSessionBtn.addEventListener('click', () => performSessionAction('start'));
stopSessionBtn.addEventListener('click', () => performSessionAction('stop'));

// Intelligent Polling
async function fetchContextStatus() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_BASE}/context/status`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        
        if (res.ok) {
            let colorClass = "";
            let pinger = "🧠";
            
            if (data.alert === "long_session" || data.alert === "check_in") {
                colorClass = "alert-warning";
                pinger = "⚠️";
            }
            if (data.alert === "goal_check") pinger = "🎯";
            if (data.alert === "auto_stop") pinger = "🛑";

            aiSuggestionBox.innerHTML = `<p class="${colorClass}">${pinger} ${data.suggestion}</p>`;
            
            // Phase 8 Integrations
            if (data.alert === "check_in") {
                pingBtn.classList.remove('hidden'); // Show ping button!
                sessionMessage.innerText = "Waiting for your response 🟡";
            }
            if (data.alert === "auto_stop") {
                // UI gracefully resets due to backend auto-stopping
                startSessionBtn.classList.remove('hidden');
                stopSessionBtn.classList.add('hidden');
                pingBtn.classList.add('hidden');
                sessionMessage.innerText = "System Auto-Stopped your session.";
            }

            if (data.status !== "inactive" && data.alert !== "auto_stop") {
                startSessionBtn.classList.add('hidden');
                stopSessionBtn.classList.remove('hidden');
            }
        }
    } catch (err) {
        console.error("Failed to fetch context.");
    }
}

function startContextEngine() {
    if (!contextInterval) {
        fetchContextStatus();
        contextInterval = setInterval(fetchContextStatus, 15000); // Live sync every 15s
    }
}

function stopContextEngine() {
    if (contextInterval) {
        clearInterval(contextInterval);
        contextInterval = null;
    }
}

checkAuth();
