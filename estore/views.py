import aiohttp.web
import uuid
import json
import aiohttp_session

class Request(object):
    def __init__(self, req):
        self._req = req
class Handler(object):
    def __init__(self, db):
        self._db = db
    async def add_event(self, req):
        stream = req.match_info['stream']
        name = req.match_info['name']
        body = await req.text()
        version = req.headers['Event-Version']
        headers = {}
        for header in req.headers:
            if header.startswith('ES-'):
                headers[header.split('-',1)[:1]] = req.headers(header)
        print("Working!")
        await self._db.add_event(stream, version, name, body, headers)
        return aiohttp.web.Response(text='Working')

    async def get_events(self, req):
        session = await aiohttp_session.get_session(req)
        session['test'] = 'dzialano'
        stream = req.match_info['stream']
        data = await self._db.get_events(stream)
        output = []
        for row in data:
            output.append({
                'id': str(row['id']),
                'stream': str(row['stream']),
                'name': row['name'],
                'version': row['version'],
                'body': row['body'],
                'headers': row['headers']})
        return aiohttp.web.json_response(output)
    async def subscribe(self, req):
        pass

async def index(db, req):
    await db.add_event(uuid.uuid4(), 1, 'user.updated', 'body', {'sth':'diabli'})
    return aiohttp.web.Response(text='Working')
