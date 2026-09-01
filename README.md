# 🎓 MaheHub — Student Event Management System

**MaheHub** is a high-performance, real-time event management platform. It uses a persistent **WebSocket** connection to sync event data and registration counts across all users instantly without page refreshes.

## ✨ Features
* **Real-Time Sync:** Instant updates for event approvals and registrations using Python WebSockets.
* **Cinematic UI:** Deep-dark "Netflix-inspired" aesthetic with Glassmorphism and responsive sidebars.
* **Role-Based Access:**
  * **Students:** Live feed of approved events and registration history.
  * **Organizers:** Create events, manage drafts, and propose to admins.
  * **Admins:** Review, approve, or reject pending event proposals.
* **Smart Scheduling:** Integrated with `Flatpickr` for high-end date and time selection.

## 🛠️ Tech Stack
* **Frontend:** HTML5, CSS3 (Custom Variables), JavaScript (Vanilla ES6)
* **Backend:** Python 3.10+, `websockets`, `asyncio`
* **Database:** MySQL / MariaDB (via `aiomysql`)
* **Libraries:** Flatpickr (Date/Time), Inter & Syncopate Google Fonts

## 🔄 Process Flow
1. **Connection:** `app.js` initializes a WebSocket handshake with the Python server (`ws://127.0.0.1:8080`).
2. **Auth:** Users log in; the server validates via MySQL and returns a role (`student`, `organiser`, `admin`).
3. **Organizer Path:** Organizers can "Save as Draft" or "Send to Admin."
4. **Admin Path:** Admins approve/reject events. On approval, the server triggers a **Broadcast Sync**.
5. **Student Path:** The "Live Event Feed" updates automatically for all students the moment an event is approved.

## 📂 Project Structure
```text
MaheHub/
├── server.py          # Asynchronous WebSocket server & DB logic
├── init_db.sql        # MySQL Schema (Users, Events, Registrations)
├── requirements.txt   # Backend dependencies
├── app.js             # Core WebSocket client & Global Auth
├── index.html         # Login & Registration gateway
├── admin.html         # Admin Approval Dashboard
├── organizer.html     # Event Proposal & Draft Portal
├── student.html       # Live Event Feed & History
└── style.css          # Cinematic Dark Mode Styling
