""" Classes for handling database connection and stuff """

import uuid
import json
import logging
import asyncio

import pypika
import psycopg2.errors
import asyncstdlib.itertools

import estore.base.event
import estore.server.db
import estore.server.query


LOGGER = logging.getLogger(__name__)


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
    return estore.base.Event(
        name=item[3],
        stream=item[1],
        headers=json.loads(item[5]),
        created=item[7],
        data=json.loads(item[4]),
        version=item[2])


class EventsQueue:
    def __init__(self, store, collection_factory):
        self.__store = store
        self.__collection_factory = collection_factory

    def __getitem__(self, item):
        if isinstance(item, uuid.UUID):
            return self.__collection_factory.stream_snapshot(item)

        if isinstance(item, slice):
            if item.stop:
                return self.__collection_factory.events_only(item)
            return self.__collection_factory.events_queue_range(item)

    def __aiter__(self):
        return self.__store.subscribe()


class EventsQueueRange:
    def __init__(self, store, query, database):
        self.__query = query
        self.__store = store
        self.__database = database

    def __getitem__(self, item):
        pass

    def __aiter__(self):
        return asyncstdlib.itertools.chain(
            estore.server.db.iterator(self.__database, str(self.__query), item_factory=row_to_event),self.__store.subscribe())


class EventsOnly:
    def __init__(self, query, database):
        self.__query = query
        self.__database = database

    def __getitem__(self, item):
        pass

    def __aiter__(self):
        pass


class StreamSnapshot:
    def __init__(self, query, database, stream_id):
        self.__query = query
        self.__database = database
        self.__stream_id = stream_id

    def __getitem__(self, item):
        if isinstance(item, slice):
            return Stream(estore.server.query.stream(self.__stream).getitem(item))

    def __aiter__(self):
        return estore.server.db.iterator(self.__database, str(self.__query), item_factory=row_to_event)


class Stream:
    def __init__(self, query, database):
        self.__query = query
        self.__database = database

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(self.__query.getitem(item), self.__database)

    def __aiter__(self):
        return estore.server.db.iterator(self.__database, str(self.__query), item_factory=row_to_event)


class CollectionFactory:
    def __init__(self, store, database):
        self.__store = store
        self.__database = database

    def stream(self, stream_id, item):
        return Stream(estore.server.query.stream(stream_id), self.__database)

    def stream_snapshot(self, stream_id):
        return StreamSnapshot(estore.server.query.stream_snapshot(stream_id), self.__database, stream_id)

    def events_only(self, item):
        return EventsOnly(estore.server.query.events().getitem(item), self.__database)

    def events_queue(self):
        return EventsQueue(self.__store, self)

    def events_queue_range(self, item):
        return EventsQueueRange(self.__store, estore.server.query.events().getitem(item), self.__database)


class Store:
    """Store class, place where all the fun begins...
    Example:
    async for event in store:
        async process_event(event)
    """
    def __init__(self, database):
        self.__database = database
        self.__consumers = []
        collection_factory = CollectionFactory(self, database)
        self.__event_collection = collection_factory.events_queue()

    async def __notify_consumers(self, event):
        LOGGER.info("notifying consumers %s", event)
        for consumer in self.__consumers:
            LOGGER.info("notifying consumers %s", consumer)
            await consumer.put(event)

    def subscribe(self):
        LOGGER.info("Subscribing consumer")
        queue = asyncio.Queue()
        consumer = EventConsumer(self.__unsubscribe, queue)
        self.__consumers.append(queue)
        return consumer

    def __getitem__(self, item):
        return self.__event_collection[item]

    async def append(self, event):
        await estore.server.db.insert(self.__database, 'event', {
            'stream': event.stream,
            'version': event.headers['Version'],
            'name': event.name,
            'body': json.dumps(event.data),
            'headers': json.dumps(event.headers)} )
        await self.__notify_consumers(event)

    def __unsubscribe(self, consumer):
        LOGGER.info("unsubscribing consumers %s", consumer)
        self.__consumers.remove(consumer)

    def __aiter__(self):
        LOGGER.info("Obtaining iterator")
        return getattr(self.__event_collection, '__aiter__')()
