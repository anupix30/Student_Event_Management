const WS_URL = 'ws://127.0.0.1:8080';
let socket;

// Current user state
let currentUser = JSON.parse(localStorage.getItem('mahehub_user'));

function initWebSocket() {
    socket = new WebSocket(WS_URL);
    
    socket.onopen = () => {
        console.log('Connected to WebSocket server');
    };
    
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data);
        
        if (data.type === 'sync') {
            // Document dispatch event so specific pages can update UI
            const syncEvent = new CustomEvent('mahehub_sync', { detail: data });
            document.dispatchEvent(syncEvent);
        } else {
            // Action response (login, register, etc.)
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
        alert('Server is disconnected. Please wait.');
        return;
    }
    
    const payload = {
        action: action,
        correlation_id: Date.now().toString(),
        ...data
    };
    
    socket.send(JSON.stringify(payload));
}

function checkAuth(requiredRole = null) {
    const isLoginPage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('Antigravity%20Student%20Event%20Management/');
    
    if (!currentUser) {
        if (!isLoginPage) {
            window.location.href = 'index.html';
        }
        return;
    }
    
    // Auth redirect based on role
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
        userInfoEl.textContent = `${currentUser.name} (${currentUser.role})`;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    updateHeader();
});
