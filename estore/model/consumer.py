import uuid
import collections

import psycopg2.errors

import estore.errors

def prepare_item(item):
    return collections.namedtuple('Consumer', ('id', 'name', 'current_sequence'))(*item)

class Consumer:
    def __init__(self, db):
        self.__db = db

    async def register(self, name):
        consumer_id = uuid.uuid4()
        try:
            async with self.__db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "INSERT INTO consumer (id, name) VALUES (%s, %s)", (consumer_id, name))
        except psycopg2.errors.UniqueViolation:
            raise estore.errors.AlreadyExists(f"User '{name}' already exists")
        return consumer_id

    async def get_by_name(self, name):
        async with self.__db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT id, name, current_sequence FROM consumer WHERE name=%s", (name, ))
                if not cursor.rowcount:
                    raise estore.errors.DoesNotExist(f"User '{name}' does not exist")
                return prepare_item(await cursor.fetchone())

    async def get_by_id(self, consumer_id):
        async with self.__db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT id, name, current_sequence FROM consumer WHERE id=%s", [consumer_id])
                if not cursor.rowcount:
                    raise estore.errors.DoesNotExist(f"User by id '{consumer_id}' does not exist")
                return prepare_item(await cursor.fetchone())
    async def update_current_sequence(self, consumer_id, current_sequence):
        async with self.__db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("UPDATE consumer SET current_sequence=%s WHERE id=%s", (current_sequence, consumer_id))
                if not cursor.rowcount:
                    raise estore.errors.DoesNotExist(f"User by id '{consumer_id}' does not exist")

    async def delete(self, consumer_id):
        async with self.__db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM consumer WHERE id=%s", (consumer_id, ))
                if not cursor.rowcount:
                    raise estore.errors.DoesNotExist(f"User by id '{consumer_id}' does not exist")
