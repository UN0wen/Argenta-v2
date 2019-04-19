import asyncpg
import asyncio

tables_dict = {}


async def create_pool(uri):
    pool = await asyncpg.create_pool(uri)
    return pool


async def create_tables(pool, verbose=False, connection=None):
    async with MaybeAcquire(connection, pool=pool) as con:
        for table in tables_dict:
            sql = f"""{table}(
            {tables_dict[table]}
            );"""
            if verbose:
                print(sql)
            await con.execute(sql)


# Auto release
class MaybeAcquire:
    def __init__(self, connection, *, pool):
        self.connection = connection
        self.pool = pool
        self._cleanup = False

    async def __aenter__(self):
        if self.connection is None:
            self._cleanup = True
            self._connection = c = await self.pool.acquire()
            return c
        return self.connection

    async def __aexit__(self, *args):
        if self._cleanup:
            await self.pool.release(self._connection)


class Table:
    def __init__(self, table_name, columns):
        tables_dict[table_name] = columns


