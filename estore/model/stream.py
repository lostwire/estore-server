import json
import uuid

import psycopg2.errors

import estore.errors

class Stream:
    def __init__(self, database):
        self.__database = database

    async def create(self, stream_id, data):
        if not isinstance(stream_id, uuid.UUID):
            try:
                stream_id = uuid.UUID(stream_id)
            except ValueError:
                raise ValueError(f"provided stream_id '{stream_id}' should be a valid UUID hexadecimal string")
        data = json.dumps(data)
        try:
            async with self.__database.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "INSERT INTO stream (id, data) VALUES (%s, %s)", stream_id, data)
        except psycopg2.errors.UniqueViolation:
            raise estore.errors.AlreadyExists(f"Stream '{stream_id}' already exists")
