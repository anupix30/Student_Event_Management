import asyncio
import json
import websockets
import aiomysql

CONNECTED_CLIENTS = set()

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'db': 'mahehub',
    'autocommit': True
}

async def get_db_pool():
    return await aiomysql.create_pool(**DB_CONFIG)

async def broadcast_sync(pool):
    if not CONNECTED_CLIENTS:
        return
        
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT e.*, u.name as organiser_name FROM events e JOIN users u ON e.organiser_id = u.id")
                events = await cur.fetchall()
                
                formatted_events = []
                for e in events:
                    e['date'] = str(e['date']) if e['date'] else ''
                    e['time'] = str(e['time']) if e['time'] else ''
                    
                    await cur.execute("SELECT COUNT(*) as count FROM registrations WHERE event_id = %s", (e['id'],))
                    reg_count = await cur.fetchone()
                    e['registration_count'] = reg_count['count']
                    
                    formatted_events.append(e)
                
                await cur.execute("SELECT status, COUNT(*) as count FROM events GROUP BY status")
                stats_rows = await cur.fetchall()
                stats = {row['status']: row['count'] for row in stats_rows}
                
                payload = {
                    'type': 'sync',
                    'events': formatted_events,
                    'stats': stats
                }
                
                message = json.dumps(payload)
                
                if hasattr(websockets, 'broadcast'):
                    websockets.broadcast(CONNECTED_CLIENTS, message)
                else:
                    for client in CONNECTED_CLIENTS:
                        try:
                            await client.send(message)
                        except Exception:
                            pass
                            
    except Exception as e:
        print(f"Broadcast error: {e}")

async def handle_register(conn, data) -> dict:
    response = {'success': False, 'message': 'Unknown error'}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    if role == 'organizer':
        role = 'organiser'
        
    dept = data.get('dept')
    reg_no = data.get('reg_no')
    
    year_str = data.get('year')
    year = int(year_str) if year_str and str(year_str).strip() else None
    
    try:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO users (name, email, password, role, dept, reg_no, year)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, email, password, role, dept, reg_no, year))
            user_id = cur.lastrowid
            response = {'success': True, 'user_id': user_id, 'role': role, 'name': name}
    except Exception as e:
        print(f"Register Error: {e}")
        response = {'success': False, 'message': 'Registration failed. Email might already exist.'}
    return response

async def handle_login(conn, data) -> dict:
    response = {'success': False, 'message': 'Unknown error'}
    email = data.get('email')
    password = data.get('password')
    
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id, name, role FROM users WHERE email = %s AND password = %s", (email, password))
            user = await cur.fetchone()
            
            if user:
                response = {'success': True, 'user_id': user['id'], 'role': user['role'], 'name': user['name']}
            else:
                response = {'success': False, 'message': 'Invalid credentials'}
    except Exception as e:
         print(f"Login Error: {e}")
         response = {'success': False, 'message': 'Database error'}
    return response

async def handle_propose_event(conn, data) -> dict:
    response = {'success': False, 'message': 'Unknown error'}
    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    time = data.get('time')
    organiser_id = data.get('organiser_id')
    is_draft = data.get('is_draft', False)
    
    status = 'draft' if is_draft else 'pending'
    
    if not date or str(date).strip() == "": date = None
    if not time or str(time).strip() == "": time = None
    
    try:
         async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO events (title, description, date, time, status, organiser_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, description, date, time, status, organiser_id))
            response = {'success': True, 'is_draft': is_draft}
    except Exception as e:
         print(f"Propose Event Error: {e}")
         response = {'success': False, 'message': str(e)}
    return response

async def handle_update_draft(conn, data) -> dict:
    response = {'success': False, 'message': 'Unknown error'}
    event_id = data.get('event_id')
    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    time = data.get('time')
    is_draft = data.get('is_draft', False)
    
    status = 'draft' if is_draft else 'pending'
    
    if not date or str(date).strip() == "": date = None
    if not time or str(time).strip() == "": time = None
    
    try:
         async with conn.cursor() as cur:
            await cur.execute("""
                UPDATE events 
                SET title=%s, description=%s, date=%s, time=%s, status=%s
                WHERE id=%s
            """, (title, description, date, time, status, event_id))
            response = {'success': True, 'is_draft': is_draft}
    except Exception as e:
         print(f"Update Draft Error: {e}")
         response = {'success': False, 'message': str(e)}
    return response

async def handle_update_event_status(conn, data) -> dict:
    response = {'success': False, 'message': 'Unknown error'}
    event_id = data.get('event_id')
    status = data.get('status')
    
    try:
         async with conn.cursor() as cur:
            await cur.execute("UPDATE events SET status = %s WHERE id = %s", (status, event_id))
            response = {'success': True}
    except Exception as e:
         print(f"Update Event Status Error: {e}")
         response = {'success': False, 'message': str(e)}
    return response

async def handle_register_event(conn, data) -> dict:
    response = {'success': False, 'message': 'Unknown error'}
    student_id = data.get('student_id')
    event_id = data.get('event_id')
    
    try:
         async with conn.cursor() as cur:
            await cur.execute("INSERT INTO registrations (student_id, event_id) VALUES (%s, %s)", (student_id, event_id))
            response = {'success': True}
    except Exception as e:
         print(f"Register Event Error: {e}")
         response = {'success': False, 'message': 'Already registered or database error'}
    return response

async def handle_fetch_history(conn, data) -> dict:
    response = {'success': False, 'message': 'Unknown error', 'history': []}
    user_id = data.get('user_id')
    role = data.get('role')
    
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            if role == 'student':
                await cur.execute("""
                    SELECT e.*, u.name as organiser_name, r.registration_time
                    FROM registrations r
                    JOIN events e ON r.event_id = e.id
                    JOIN users u ON e.organiser_id = u.id
                    WHERE r.student_id = %s
                    ORDER BY r.registration_time DESC
                """, (user_id,))
                events = await cur.fetchall()
                for e in events:
                    e['date'] = str(e['date']) if e['date'] else '-'
                    e['time'] = str(e['time']) if e['time'] else '-'
                    e['registration_time'] = str(e['registration_time'])
                response = {'success': True, 'history': events}
                
            elif role == 'organiser' or role == 'organizer':
                 await cur.execute("SELECT * FROM events WHERE organiser_id = %s ORDER BY id DESC", (user_id,))
                 events = await cur.fetchall()
                 for e in events:
                    e['date'] = str(e['date']) if e['date'] else ''
                    e['time'] = str(e['time']) if e['time'] else ''
                 response = {'success': True, 'history': events}
    except Exception as e:
        print(f"Fetch History Error: {e}")
        response = {'success': False, 'message': str(e)}
    return response

async def connection_handler(websocket, pool):
    CONNECTED_CLIENTS.add(websocket)
    try:
        await broadcast_sync(pool)
        
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get('action')
                
                async with pool.acquire() as conn:
                    response_dict = {}
                    needs_broadcast = False
                    
                    if action == 'register':
                        response_dict = await handle_register(conn, data)
                    elif action == 'login':
                        response_dict = await handle_login(conn, data)
                    elif action == 'propose_event':
                        response_dict = await handle_propose_event(conn, data)
                        needs_broadcast = response_dict.get('success', False)
                    elif action == 'update_draft':
                        response_dict = await handle_update_draft(conn, data)
                        needs_broadcast = response_dict.get('success', False)
                    elif action == 'update_event_status':
                        response_dict = await handle_update_event_status(conn, data)
                        needs_broadcast = response_dict.get('success', False)
                    elif action == 'register_event':
                        response_dict = await handle_register_event(conn, data)
                        needs_broadcast = response_dict.get('success', False)
                    elif action == 'fetch_history':
                        response_dict = await handle_fetch_history(conn, data)
                        
                    if isinstance(response_dict, dict) and len(response_dict) > 0:
                        response_dict['correlation_id'] = data.get('correlation_id')
                        response_dict['action_response'] = action
                        await websocket.send(json.dumps(response_dict))
                        
                    if needs_broadcast:
                        await broadcast_sync(pool)
                        
            except Exception as e:
                print(f"Error handling message payload: {e}")
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"Connection handler error: {e}")
    finally:
        CONNECTED_CLIENTS.remove(websocket)

async def main():
    pool = await get_db_pool()
    
    async def handler(websocket):
        await connection_handler(websocket, pool)
        
    print("Starting WebSocket server on ws://127.0.0.1:8080...")
    
    stop_event = asyncio.Event()
    try:
        async with websockets.serve(handler, "127.0.0.1", 8080):
            await stop_event.wait()
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer has been gracefully stopped. Goodbye!")
