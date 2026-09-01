# MAHEHub — Student Event Management System

MAHEHub is a role-based student event management web application designed to simplify the creation, approval, discovery, and registration of campus events.

The system provides separate workflows for Students, Event Organizers, and Administrators. It uses a Python WebSocket backend to maintain real-time communication and synchronization between connected clients, with SQLite used for persistent application data.

## Live Deployment

The backend WebSocket service is deployed on Render.

**Hosting Platform:** Render  
**Service Type:** Web Service  
**Live Backend / WebSocket Endpoint:**  
https://mahehub-backend.onrender.com

The deployed service uses a secure WebSocket connection (`wss://`) for public communication.

> Note: The repository contains the static frontend pages under `frontend/`. The public Render deployment described above is the backend/WebSocket service. When running the frontend, configure its WebSocket endpoint to either the local development server or the deployed Render endpoint.

---

## Project Overview

Campus events often involve multiple participants and approval stages. MAHEHub provides a centralized system where:

- Students can discover approved events and register for them.
- Organizers can create and submit events for approval.
- Administrators can review, approve, or reject submitted events.
- Connected clients receive synchronized event data through WebSocket communication.
- Event registration information is stored persistently in the database.
- Approved events can be pushed to connected student clients in real time.

The project demonstrates the integration of a static web frontend, asynchronous Python backend, WebSocket-based real-time communication, and database management into a single application.

---

## Key Features

### Student

- Student authentication and registration
- View available/live events
- Register for events
- Receive synchronized event information
- View event-related information such as:
  - Event name
  - Organizing club
  - Description
  - Date
  - Time
  - Registration information

### Event Organizer

- Organizer authentication
- Create and submit new events
- Provide event details including date and time
- Submit events for administrator review
- Track event status through the application workflow

### Administrator

- Administrator authentication
- View submitted events
- Review pending events
- Approve or reject events
- Make approved events available to students
- Trigger real-time synchronization after event decisions

### Real-Time Communication

MAHEHub uses WebSockets to maintain a persistent, bidirectional communication channel between the browser and the Python backend.

This allows the server to:

- Broadcast updated event data to connected clients
- Synchronize event state across multiple users
- Notify students when an event becomes live/approved
- Update registration information without relying on repeated page polling

---

## System Architecture

```text
                    ┌─────────────────────────┐
                    │      MAHEHub Users       │
                    │                         │
                    │  Student / Organizer /  │
                    │       Admin             │
                    └────────────┬────────────┘
                                 │
                                 │
                         HTML / CSS / JavaScript
                                 │
                                 │ WebSocket
                                 │ ws:// or wss://
                                 ▼
                    ┌─────────────────────────┐
                    │   Python WebSocket      │
                    │        Server           │
                    │                         │
                    │  • Authentication       │
                    │  • Event Management     │
                    │  • Registration         │
                    │  • Event Decisions      │
                    │  • Data Synchronization │
                    │  • Client Broadcasting  │
                    └────────────┬────────────┘
                                 │
                                 │ SQL
                                 ▼
                    ┌─────────────────────────┐
                    │         SQLite          │
                    │                         │
                    │       campus.db         │
                    │                         │
                    │  • Users                │
                    │  • Events               │
                    │  • Registrations        │
                    └─────────────────────────┘
```

### Communication Flow

```text
Organizer
    │
    │ Create Event
    ▼
Python WebSocket Server
    │
    │ Store Event
    ▼
SQLite Database
    │
    │ Synchronize
    ▼
Administrator
    │
    │ Approve / Reject
    ▼
Python WebSocket Server
    │
    │ Broadcast Update
    ▼
Connected Students
    │
    │ Register
    ▼
SQLite Database
    │
    │ Registration Update
    ▼
Connected Clients
```

---

## Real-Time Event Workflow

1. An organizer submits a new event.
2. The Python backend receives the request through WebSocket communication.
3. The event is stored in the SQLite database.
4. Connected clients receive synchronized application data.
5. An administrator reviews the submitted event.
6. The administrator approves or rejects the event.
7. When approved, the event becomes available to students.
8. Connected student clients can receive the approved-event update in real time.
9. Students can register for the event.
10. Registration information is stored and synchronized with connected clients.

---

## WebSocket Communication

One of the main technical components of MAHEHub is its WebSocket-based backend.

Instead of repeatedly requesting the server for updates, the application maintains a persistent connection between the browser and the server.

### Why WebSockets?

WebSockets were selected because the application requires real-time, bidirectional communication.

They allow:

- Persistent client-server connections
- Server-initiated updates
- Real-time event synchronization
- Reduced dependence on polling
- Broadcasting updates to multiple connected clients

For local development, WebSocket communication uses a local endpoint such as:

```text
ws://localhost:3000
```

For the deployed application:

```text
wss://mahehub-backend.onrender.com
```

---

## Application Message Flow

The backend handles different message types for different operations.

### Client Requests

```text
STUDENT_AUTH
REGISTER
NEW_EVENT_REQUEST
STUDENT_REGISTER
EVENT_DECISION
```

### Server Responses / Events

```text
SYNC_DATA
POST_LIVE_EVENT
```

These messages allow the frontend and backend to communicate using structured WebSocket events rather than traditional page-refresh-based workflows.

---

## Database

MAHEHub currently uses SQLite for persistent data storage.

The database is stored in:

```text
db_storage/campus.db
```

### Main Tables

#### `users`

Stores user account and role information.

```text
email
username
password
role
```

#### `events`

Stores event information.

```text
id
name
club
description
status
date
time
created_at
```

#### `registrations`

Stores student registrations for events.

```text
id
event_id
student_email
```

The backend also retrieves registration counts alongside event information to support event-related functionality.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python |
| Server Model | Python AsyncIO |
| Real-Time Communication | WebSockets |
| Database | SQLite |
| Protocol | WebSocket |
| Local WebSocket | `ws://` |
| Production WebSocket | `wss://` |
| Hosting | Render |
| Version Control | Git / GitHub |

---

## Frontend

The frontend is implemented using static HTML, CSS, and JavaScript.

Role-specific pages provide separate interfaces for:

```text
login.html       → Authentication
student.html     → Student dashboard
organizer.html   → Organizer dashboard
admin.html       → Administrator dashboard
```

The frontend communicates with the backend using WebSockets.

The application uses a modern, visually focused interface inspired by streaming-platform style layouts while keeping the implementation lightweight with standard web technologies.

---

## Backend

The backend is implemented in Python using asynchronous programming and the `websockets` library.

The main server is:

```text
server.py
```

The backend is responsible for:

- Accepting WebSocket connections
- Handling authentication requests
- Managing connected clients
- Processing event creation requests
- Processing student registrations
- Handling administrator event decisions
- Reading and writing database records
- Broadcasting synchronized data
- Sending live event notifications

The asynchronous server model allows the application to handle multiple WebSocket connections concurrently.

---

## Repository Structure

```text
Student_Event_Management/
│
├── frontend/
│   ├── login.html
│   ├── student.html
│   ├── organizer.html
│   └── admin.html
│
├── db_storage/
│   └── campus.db
│
├── server.py
├── requirements.txt
└── README.md
```

---

## Installation and Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/anupv30/Student_Event_Management.git
```

### 2. Navigate to the Project

```bash
cd Student_Event_Management
```

### 3. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If using Command Prompt:

```cmd
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Start the Backend

```bash
python server.py
```

The backend can then be accessed through the WebSocket endpoint configured for local development.

For the standard local configuration:

```text
ws://localhost:3000
```

### 7. Run the Frontend

Open the appropriate HTML page from the `frontend/` directory.

Make sure the frontend WebSocket URL matches the backend you are using.

For local development:

```text
ws://localhost:3000
```

For the deployed backend:

```text
wss://mahehub-backend.onrender.com
```

---

## Deployment

The backend is deployed as a Render Web Service.

### Deployment Configuration

```text
Platform: Render
Service Type: Web Service

Build Command:
pip install -r requirements.txt

Start Command:
python server.py
```

### Production Endpoint

```text
wss://mahehub-backend.onrender.com
```

The production deployment uses a secure WebSocket connection (`wss://`) for communication between clients and the hosted backend.

The deployment allows the application backend to be accessed over the public internet rather than only from a local development environment.

---

## Performance Testing

The deployed WebSocket service was tested using a custom asynchronous concurrency test against the public Render endpoint.

The test measured the response time for WebSocket clients performing the registration/synchronization interaction.

### Stable Concurrency Results

| Concurrent Clients | Success | Average | Median (P50) | P95 |
|---:|---:|---:|---:|---:|
| 100 | 100/100 | 357.91 ms | 351.00 ms | 410.23 ms |
| 200 | 200/200 | 358.64 ms | 375.17 ms | 479.85 ms |
| 250 | 250/250 | 368.15 ms | 385.43 ms | 501.18 ms |
| 300 | 300/300 | 487.87 ms | 362.65 ms | 857.39 ms |
| 350 | 350/350 | 338.53 ms | 353.76 ms | 501.88 ms |
| 400 | 400/400 | 383.15 ms | 391.12 ms | 572.62 ms |

### Highlight

At **400 concurrent clients**, the deployed service achieved:

```text
Successful Clients : 400 / 400
Success Rate       : 100%
Average Latency    : 383.15 ms
Median Latency     : 391.12 ms
P95 Latency        : 572.62 ms
Maximum Latency    : 584.17 ms
```

This demonstrates that the deployed application was able to successfully maintain and process a burst of 400 concurrent WebSocket client interactions during the test.

### Latency Definitions

**Average latency**  
The mean response time across all successful requests.

**Median / P50**  
50% of measured requests completed within this time.

**P95**  
95% of measured requests completed within this time, while the slowest 5% took longer.

Lower latency indicates faster request/response completion.

> These figures are measurements from a synthetic WebSocket concurrency test against the deployed service. They should not be interpreted as a formal production capacity limit or benchmark of all application operations.

### Higher Concurrency

During testing, connection failures were observed at higher burst levels, particularly around 450–500 concurrent clients.

Therefore, the project does **not** claim 500 concurrent clients as a supported capacity.

The 400-client result is used as the reliable benchmark because it achieved 100% successful connections in the recorded test.

---

## Testing Approach

The performance test used asynchronous client connections to simulate multiple users connecting to the deployed WebSocket server.

The test focused on:

- WebSocket connection establishment
- Concurrent client handling
- Message exchange
- Registration/synchronization response
- Response latency
- Success rate
- Median latency
- P95 latency

This provides a practical indication of how the current deployed configuration behaves under concurrent WebSocket activity.

---

## Security Considerations

The current project is primarily designed as an academic/hackathon application.

For production deployment, additional security improvements would be required, including:

- Password hashing instead of storing plaintext passwords
- Moving administrative credentials and secrets into environment variables
- Stronger authentication and session management
- Input validation and sanitization
- Rate limiting
- WebSocket connection authentication
- Secure authorization checks for every role-sensitive operation
- Database access hardening
- HTTPS security headers for the frontend
- Logging and monitoring of authentication and administrative operations

These improvements are planned areas for future development.

---

## Current Limitations

The current implementation has several practical limitations:

- SQLite is suitable for the current project scale but is not ideal for a large multi-instance production deployment.
- The current deployment can experience connection failures during very large connection bursts.
- The frontend is provided as static HTML/CSS/JavaScript.
- Production-grade authentication and credential management would require additional security hardening.
- Horizontal scaling would require shared state/message broadcasting between backend instances.

---

## Future Enhancements

Potential future improvements include:

- Migration from SQLite to MySQL or PostgreSQL for production-scale workloads
- Secure password hashing
- Environment-based secret management
- JWT/session-based authentication
- Email notifications for event approvals and registrations
- Event search and filtering
- Event categories
- Calendar integration
- Organizer analytics
- Student registration history
- QR-code-based event check-in
- Admin analytics dashboard
- Redis-based WebSocket/pub-sub synchronization
- Docker containerization
- CI/CD pipeline
- Automated testing
- Structured logging and monitoring
- Rate limiting and connection management
- Dedicated production frontend deployment
- More comprehensive load testing using tools such as Locust or k6

---

## Project Highlights

MAHEHub demonstrates practical implementation of:

- Role-based application design
- Full-stack web development
- Client-server architecture
- Asynchronous Python programming
- Real-time WebSocket communication
- Database-backed application development
- Multi-client synchronization
- Event approval workflows
- Concurrent connection handling
- Cloud deployment using Render
- Performance testing of a deployed application

---

## Why WebSockets Were Used

Traditional polling requires the browser to repeatedly ask the server whether new information is available.

MAHEHub instead maintains a persistent WebSocket connection.

This makes it possible for the server to immediately send relevant updates to connected clients when:

- An event is created
- An event is approved
- An event is rejected
- A student registers for an event
- Application data needs synchronization

This architecture is particularly suitable for a campus event system where multiple users may be viewing or modifying event information at the same time.

---

## Deployment Architecture

```text
             Internet Users
                   │
                   │ Secure WebSocket
                   │ wss://
                   ▼
       ┌─────────────────────────┐
       │         Render          │
       │                         │
       │  MAHEHub Backend        │
       │  Python WebSocket       │
       │  Server                 │
       └────────────┬────────────┘
                    │
                    ▼
             SQLite Database
                campus.db
```

---

## Repository

GitHub Repository:

https://github.com/anupv30/Student_Event_Management

---

## Author

**Anup V**

GitHub:

https://github.com/anupv30

---

## Project Status

**Status:** Deployed and functional

**Backend:** Live on Render

**Real-Time Communication:** WebSocket

**Database:** SQLite

**Tested Concurrency:** 400 concurrent clients with 100% success in the recorded benchmark

---

## License

No open-source license has currently been specified for this repository.
