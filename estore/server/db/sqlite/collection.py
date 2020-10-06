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
