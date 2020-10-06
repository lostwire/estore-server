import estore.server.base

async def row_to_event(item):
    return estore.base.Event(
        name=item[3],
        stream=item[1],
        headers=item[5],
        created=item[7],
        data=json.loads(item[4]),
        version=item[2])

class EventsQueue(estore.server.base.Collection):
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


class EventsQueueRange(estore.server.base.Collection):
    def __init__(self, store, query, database):
        self.__query = query
        self.__store = store
        self.__database = database

    def __getitem__(self, item):
        pass

    def __aiter__(self):
        return asyncstdlib.itertools.chain(
            estore.server.db.iterator(self.__database, str(self.__query), item_factory=row_to_event),self.__store.subscribe())


class EventsOnly(estore.server.base.Collection):
    def __init__(self, query, database):
        self.__query = query
        self.__database = database

    def __getitem__(self, item):
        pass

    def __aiter__(self):
        pass


class StreamSnapshot(estore.server.base.Collection):
    def __init__(self, query, database, stream_id):
        self.__query = query
        self.__database = database
        self.__stream_id = stream_id

    def __getitem__(self, item):
        if isinstance(item, slice):
            return Stream(estore.server.query.stream(self.__stream).getitem(item))

    def __aiter__(self):
        return estore.server.db.iterator(self.__database, str(self.__query), item_factory=row_to_event)


class Stream(estore.server.base.Collection):
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
        return EvensQueue(self.__store, self)

    def events_queue_range(self, item):
        return EventsQueueRange(self.__store, estore.server.query.events().getitem(item), self.__database)
