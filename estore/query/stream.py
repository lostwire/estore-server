import estore.errors

class Stream:
    def __init__(self, database):
        self.__database = database

    async def get_by_id(self, stream_id):
        cursor = await self.__database.execute("SELECT id, name, data FROM stream WHERE id=%s", stream_id, dict_cursor=True)
        if not cursor.rowcount:
            raise estore.errors.DoesNotExist(f"Stream '{stream_id}' does not exist")
        return cursor.fetchone()

    async def get_by_name(self, stream_name):
        cursor = await self.__database.execute("SELECT id, name, data FROM stream WHERE id=%s", stream_name, dict_cursor=True)
        if not cursor.rowcount:
            raise estore.errors.DoesNotExist(f"Stream '{stream_name}' does not exist")
        return cursor.fetchone()
