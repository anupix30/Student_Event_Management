const WS_URL = 'ws://127.0.0.1:8080';
let socket;

let currentUser = JSON.parse(localStorage.getItem('mahehub_user'));

function showToast(title, message, icon = '✦') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <div class="toast-body">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hiding');
        toast.addEventListener('animationend', () => toast.remove());
    }, 3500);
}

function initWebSocket() {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        console.log('Connected to WebSocket server');
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data);

        if (data.type === 'sync') {
            const syncEvent = new CustomEvent('mahehub_sync', { detail: data });
            document.dispatchEvent(syncEvent);
        } else {
            const responseEvent = new CustomEvent(`mahehub_response_${data.action_response}`, { detail: data });
            document.dispatchEvent(responseEvent);
        }
    };

    socket.onclose = () => {
        console.log('WebSocket disconnected. Reconnecting in 3s...');
        setTimeout(initWebSocket, 3000);
    };
}

function sendAction(action, data) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error('WebSocket is not connected');
        return; // silently fail — no alert
    }

    const payload = {
        action: action,
        correlation_id: Date.now().toString(),
        ...data
    };

    socket.send(JSON.stringify(payload));
}

function checkAuth(requiredRole = null) {
    const isLoginPage = window.location.pathname.endsWith('index.html')
        || window.location.pathname === '/'
        || window.location.pathname.endsWith('Antigravity%20Student%20Event%20Management/');

    if (!currentUser) {
        if (!isLoginPage) window.location.href = 'index.html';
        return;
    }

    if (isLoginPage) {
        if (currentUser.role === 'admin') window.location.href = 'admin.html';
        else if (currentUser.role === 'organiser') window.location.href = 'organizer.html';
        else if (currentUser.role === 'student') window.location.href = 'student.html';
    } else if (requiredRole && currentUser.role !== requiredRole) {
        window.location.href = 'index.html';
    }
}

function logout() {
    localStorage.removeItem('mahehub_user');
    window.location.href = 'index.html';
}

function updateHeader() {
    const userInfoEl = document.getElementById('user-info-name');
    if (userInfoEl && currentUser) {
        userInfoEl.textContent = currentUser.name;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    updateHeader();
});
