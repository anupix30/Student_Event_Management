import asyncio
import json
import websockets
import sqlite3
import os

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOLDER = os.path.join(BASE_DIR, "db_storage")
DB_NAME = "campus.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

def init_db():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Events Table - UPDATED with date and time columns to fix TBA issue
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            club TEXT,
            description TEXT,
            status TEXT DEFAULT 'pending',
            date TEXT,
            time TEXT,
            created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))
        )
    ''')
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student'
        )
    ''')

    # Registrations Table (New)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT,
            student_email TEXT,
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_to_db(payload):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # UPDATED to include date and time from the Organizer's payload
        cursor.execute('''
            INSERT INTO events (id, name, club, description, status, date, time) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (payload['id'], payload['name'], payload['club'], payload['desc'], 'pending', payload.get('date'), payload.get('time')))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Event ID {payload['id']} already exists.")
    finally:
        conn.close()

def fetch_all_events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # UPDATED Query: Now pulls date and time along with the registration count
    cursor.execute('''
        SELECT e.id, e.name, e.club, e.description, e.status, COUNT(r.id) as reg_count, e.date, e.time
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.id
        ORDER BY e.created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    # UPDATED Mapping: r[6] is date and r[7] is time
    return [{"id": r[0], "name": r[1], "club": r[2], "desc": r[3], "status": r[4], "reg_count": r[5], "date": r[6], "time": r[7]} for r in rows]

# --- WEBSOCKET LOGIC ---

CLIENTS = {} # {websocket: role}

async def broadcast_sync():
    """Pushes the entire events list to EVERYONE connected."""
    all_data = fetch_all_events()
    message = json.dumps({"type": "SYNC_DATA", "payload": all_data})
    
    for ws in list(CLIENTS.keys()):
        try:
            await ws.send(message)
        except:
            if ws in CLIENTS:
                del CLIENTS[ws]

async def handle_connection(websocket):
    CLIENTS[websocket] = None
    
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            # 1. AUTHENTICATION (Fixed for Student Login/Registration)
            if msg_type == "STUDENT_AUTH":
                email = data.get("email")
                password = data.get("password")
                username = data.get("username")
                
                # Special Admin List
                ALLOWED_ADMINS = ["tejasnj14@gmail.com", "anupvenu@gmail.com", "abhay.sg2006@gmail.com"]
                MASTER_PASS = os.environ.get("MASTER_PASS", "12345678")

                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT username, password, role FROM users WHERE email = ?', (email,))
                user = cursor.fetchone()

                if not user:
                    if not username:
                        await websocket.send(json.dumps({"type": "AUTH_RESPONSE", "status": "not_found"}))
                    else:
                        cursor.execute('INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)', 
                                     (email, username, password, 'student'))
                        conn.commit()
                        await websocket.send(json.dumps({
                            "type": "AUTH_RESPONSE", "status": "success", 
                            "user": {"email": email, "username": username, "role": "student"}
                        }))
                else:
                    db_username, db_password, db_role = user
                    if (email in ALLOWED_ADMINS and password == MASTER_PASS) or (db_password == password):
                        await websocket.send(json.dumps({
                            "type": "AUTH_RESPONSE", "status": "success", 
                            "user": {"email": email, "username": db_username, "role": db_role}
                        }))
                    else:
                        await websocket.send(json.dumps({"type": "AUTH_RESPONSE", "status": "error", "message": "Incorrect Password"}))
                conn.close()

            # 2. ROLE REGISTRATION
            elif msg_type == "REGISTER":
                CLIENTS[websocket] = data.get("role")
                all_data = fetch_all_events()
                await websocket.send(json.dumps({"type": "SYNC_DATA", "payload": all_data}))

            # 3. NEW EVENT
            elif msg_type == "NEW_EVENT_REQUEST":
                save_to_db(data['payload'])
                await broadcast_sync()

            # 4. STUDENT REGISTRATION (New Logic)
            elif msg_type == "STUDENT_REGISTER":
                event_id = data.get("event_id")
                student_email = data.get("email")
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM registrations WHERE event_id = ? AND student_email = ?', (event_id, student_email))
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO registrations (event_id, student_email) VALUES (?, ?)', (event_id, student_email))
                    conn.commit()
                conn.close()
                await broadcast_sync()

            # 5. ADMIN DECISION
            elif msg_type == "EVENT_DECISION":
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('UPDATE events SET status = ? WHERE id = ?', (data['status'], data['id']))
                conn.commit()
                
                # UPDATED to fetch date/time for the live notification
                cursor.execute('SELECT id, name, club, description, status, date, time FROM events WHERE id = ?', (data['id'],))
                updated_ev = cursor.fetchone()
                conn.close()
                
                await broadcast_sync()

                if data["status"] == "approve" and updated_ev:
                    live_msg = json.dumps({
                        "type": "POST_LIVE_EVENT", 
                        "payload": {
                            "id": updated_ev[0], 
                            "name": updated_ev[1], 
                            "club": updated_ev[2],
                            "date": updated_ev[5],
                            "time": updated_ev[6]
                        }
                    })
                    for ws, role in CLIENTS.items():
                        if role == "student":
                            try: await ws.send(live_msg)
                            except: pass

    except Exception as e:
        print(f"Socket Error: {e}")
    finally:
        if websocket in CLIENTS:
            del CLIENTS[websocket]

def reset_test_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM registrations")
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM users WHERE role = 'student'")

    conn.commit()
    conn.close()

    print("TEST DATA RESET COMPLETE")


def reset_test_data():
    if os.environ.get("RESET_DATABASE") == "true":
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM registrations")
        cursor.execute("DELETE FROM events")
        cursor.execute("DELETE FROM users WHERE role = 'student'")

        conn.commit()
        conn.close()

        print("TEST DATA RESET COMPLETE")


async def main():
    init_db()
    reset_test_data()

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 3000))
    async with websockets.serve(handle_connection, host, port):
        print(f"Campus Control Server Online: ws://{host}:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())