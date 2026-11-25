import asyncio, json, time
from collections import deque
from datetime import datetime, timezone
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, DisconnectEvent, LiveEndEvent, EnvelopeEvent, RoomUserSeqEvent

app = FastAPI(title='SANDIQ RADARI')
app.mount('/static', StaticFiles(directory='.'), name='static')
MAX_USERS = 5
clients: dict[str, TikTokLiveClient] = {}
status: dict[str, dict] = {}
events = deque(maxlen=200)
next_id = 1

class WatchRequest(BaseModel):
    usernames: list[str]

def plain(obj: Any, depth=0):
    if depth > 4: return str(obj)
    if obj is None or isinstance(obj, (str, int, float, bool)): return obj
    if isinstance(obj, dict): return {str(k): plain(v, depth+1) for k,v in obj.items()}
    if isinstance(obj, (list, tuple)): return [plain(v, depth+1) for v in obj[:40]]
    if hasattr(obj, '__dict__'):
        return {str(k): plain(v, depth+1) for k,v in vars(obj).items() if not str(k).startswith('_')}
    return str(obj)

def publish(username, kind, payload=None):
    global next_id
    events.append({'id': next_id, 'username': username, 'type': kind, 'at': int(time.time()), 'data': plain(payload or {})})
    next_id += 1

def find_number(data, keys):
    if isinstance(data, dict):
        for k,v in data.items():
            if k.lower() in keys and isinstance(v, (int,float)) and v > 0: return int(v)
        for v in data.values():
            found = find_number(v, keys)
            if found: return found
    elif isinstance(data, list):
        for v in data:
            found = find_number(v, keys)
            if found: return found
    return None

async def monitor(username):
    client = TikTokLiveClient(unique_id=username)
    clients[username] = client
    status[username] = {'username': username, 'live': False, 'connected': False, 'viewers': None, 'last_error': None, 'last_check': int(time.time())}

    @client.on(ConnectEvent)
    async def on_connect(event):
        status[username].update(live=True, connected=True, last_error=None, last_check=int(time.time()))
        publish(username, 'live_connected', {'room_id': getattr(client, 'room_id', None)})

    @client.on(DisconnectEvent)
    async def on_disconnect(event):
        status[username].update(live=False, connected=False, last_check=int(time.time()))
        publish(username, 'disconnected')

    @client.on(LiveEndEvent)
    async def on_end(event):
        status[username].update(live=False, connected=False, viewers=None)
        publish(username, 'live_ended')

    @client.on(RoomUserSeqEvent)
    async def on_viewers(event):
        raw = plain(event)
        count = find_number(raw, {' total', 'total', 'user_count', 'viewer_count', 'total_user', 'online_user_count'})
        if count is not None: status[username]['viewers'] = count
        publish(username, 'viewer_update', raw)

    @client.on(EnvelopeEvent)
    async def on_envelope(event):
        raw = plain(event)
        # Keep the exact source payload. Only show a countdown if the event explicitly supplies an expiry/open timestamp.
        expiry = find_number(raw, {'expire_time', 'end_time', 'open_time', 'available_time', 'finish_time'})
        now = int(time.time())
        if expiry and expiry > 10_000_000_000: expiry //= 1000
        countdown = max(0, expiry-now) if expiry and expiry > now else None
        publish(username, 'treasure_chest', {'raw': raw, 'opens_in_seconds': countdown, 'source_expiry': expiry})

    try:
        await client.start(fetch_room_info=True)
        if username in status:
            status[username].update(live=bool(client.connected), connected=bool(client.connected), last_check=int(time.time()))
    except Exception as exc:
        status[username].update(live=False, connected=False, last_error=str(exc)[:240], last_check=int(time.time()))
        publish(username, 'connection_error', {'message': str(exc)[:240]})
    finally:
        clients.pop(username, None)
        if username in status:
            status[username].update(live=False, connected=False, last_check=int(time.time()))

@app.get('/')
async def home():
    with open('index.html', encoding='utf-8') as f: return HTMLResponse(f.read())

@app.get('/api/status')
async def get_status(): return {'status': list(status.values()), 'events': list(events)[-60:]}

@app.post('/api/watchlist')
async def set_watchlist(req: WatchRequest):
    names=[]
    for name in req.usernames:
        n=name.strip().lstrip('@')
        if n and n not in names: names.append(n)
    if len(names)>MAX_USERS: raise HTTPException(400, 'Maksimum 5 hesab izlənə bilər.')
    for name, client in list(clients.items()):
        if name not in names:
            try: await client.disconnect()
            except Exception: pass
    for name in names:
        if name not in clients:
            asyncio.create_task(monitor(name))
    return {'ok': True, 'watching': names, 'note': 'LIVE yoxlaması qeyri-rəsmi TikTokLive bağlantısı ilə aparılır.'}

@app.get('/api/events')
async def get_events(since: int = 0): return {'events': [e for e in events if e['id'] > since]}

@app.get('/health')
async def health(): return {'ok': True, 'service': 'SANDIQ RADARI'}
