import estore.server.db.sqlite.sql

class SQLite:
    def __init__(self, connection):
        """ Initialize class
        Arguments:
            connection - sql connection
        """
        self.__connection = connection

    async def initialize(self):
        for query in estore.server.db.sqlite.sql:
            await self.__connection.execute(query)
