import uuid
import json
import asyncio
import logging

import pypika
import psycopg2.errors
import asyncstdlib.itertools

import estore.db
import estore.query


logger = logging.getLogger(__name__)

class EventConsumer:
    def __init__(self, cleanup_callback, queue):
        self.__cleanup_callback = cleanup_callback
        self.__queue = queue

    async def __anext__(self):
        return await self.__queue.get()

    def __aiter__(self):
        return self

    def __del__(self):
        self.__cleanup_callback(self.__queue)

    async def __call__(self, event):
        await self.__queue.put(event)

async def row_to_event(item):
    return Event(item[3], json.loads(item[4]), { 'version': item[2], 'id': item[0], 'seq': item[6] })

def apply_slice(query, ranges):


class EventCollection:
    def __init__(self, store, query, database, with_queue=True):
        self.__store = store
        self.__query = query
        self.__database = database
        self.__with_queue = with_queue

    def __create(self, query, with_queue=True):
        return self.__class__(self.__store, query, self.__database, with_queue=with_queue)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__create(self.__query.getitem(item), with_queue=not bool(item.stop))
        if isinstance(item, uuid.UUID):
            return self.__create(self.__query.filter.stream == str(item), with_queue=False)

    async def __length__(self):
        results = await estore.db.fetchone(self.__database, str(self.__query.length))
        return results[0]

    def __aiter__(self):
        if self.__with_queue:
            return asyncstdlib.itertools.chain(
                estore.db.iterator(self.__database, str(self.__query), item_factory=row_to_event),
                self.__store.subscribe())
        return estore.db.iterator(self.__database, str(self.__query), item_factory=row_to_event)

class StreamCollection:
    pass



class Store:
    def __init__(self, database):
        self.__database = database
        self.__consumers = []
        columns = ['id','stream','version','name','body','headers','seq']
        self.__event_collection = EventCollection(
            self,
            estore.query.QueryBuilder(pypika.Query.from_('event').select(*columns).orderby('created', order=pypika.Order.asc)),
            database)

    async def __notify_consumers(self, event):
        logger.info("notifying consumers %s", event)
        for consumer in self.__consumers:
            logger.info("notifying consumers %s", consumer)
            await consumer.put(event)

    async def __length__(self):
        return await length(self.__event_collection)

    def subscribe(self):
        queue = asyncio.Queue()
        consumer = EventConsumer(self.__unsubscribe, queue)
        self.__consumers.append(queue)
        return consumer

    async def __getitem__(self, item):
        return self.__event_collection[item]

    async def append(self, event):
        try:
            await estore.db.insert(self.__database, 'event', {
                'stream': event.stream,
                'version': event.headers['Version'],
                'name': event.name,
                'body': json.dumps(event.data),
                'headers': json.dumps(event.headers)} )
        except psycopg2.errors.ForeignKeyViolation:
            await estore.db.insert(self.__database, 'stream', {
                'id': event.stream,
                'snapshot': 0,
                'data': json.dumps({})})
            self[item] = event
        await self.__notify_consumers(event)

    def __unsubscribe(self, consumer):
        logger.info("unsubscribing consumers %s", consumer)
        self.__consumers.remove(consumer)

    def __aiter__(self):
        return getattr(self.__event_collection, '__aiter__')()


class Event:
    def __init__(self, name, data, headers):
        self.__name = name
        self.__data = data
        self.__headers = None
        self.__stream = name.split('.').pop(0)
        self.__set_headers(headers)

    @property
    def name(self):
        return self.__name

    @property
    def data(self):
        return self.__data

    @property
    def stream(self):
        return self.__stream

    @property
    def headers(self):
        return self.__headers

    @property
    def json(self):
        return json.dumps(dict(self))

    def __set_headers(self, headers):
        keys, values = zip(*headers.items())
        self.__headers = dict(zip(keys, map(str, values)))

    def dict(self):
        return {
            'name': self.__name,
            'data': self.__data,
            'headers': self.__headers }

    def __dir__(self):
        return dir(self)

    def __dict__(self):
        return self.dict()

    def __repr__(self):
        return f"Event (name: {self.name}, data: {self.data}, headers: {self.headers})"
