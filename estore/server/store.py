""" Classes for handling database connection and stuff """

import uuid
import json
import logging
import asyncio

import pypika
import psycopg2.errors
import asyncstdlib.itertools

import estore.base.event

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


class Store:
    """Store class, place where all the fun begins...
    Example:
    async for event in store:
        async process_event(event)
    """
    def __init__(self, db_engine):
        self.__db_engine = db_engine
        self.__consumers = []

    async def initialize(self):
        await self.__db_engine.initialize()

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

    async def close(self):
        await self.__db_engine.close()

    def __del__(self):
        LOGGER.info("Dying")

    def __getitem__(self, item):
        return self.__event_collection[item]

    async def append(self, event):
        await self.__db_engine.insert(event)
        await self.__notify_consumers(event)

    def __unsubscribe(self, consumer):
        LOGGER.info("unsubscribing consumers %s", consumer)
        self.__consumers.remove(consumer)

    def __aiter__(self):
        LOGGER.info("Obtaining iterator")
        return getattr(self.__event_collection, '__aiter__')()
