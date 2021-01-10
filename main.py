import logging
import bot
import contextlib
import config
import asyncio
from cogs.utils import db

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@contextlib.contextmanager
def setup_logging():
    try:
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        log = logging.getLogger()
        log.setLevel(logging.INFO)

        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')

        file_handler = logging.FileHandler(filename='argenta.log', encoding='utf-8', mode='w')
        file_handler.setFormatter(fmt)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(fmt)

        log.addHandler(file_handler)
        log.addHandler(stream_handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


def run_bot():
    loop = asyncio.get_event_loop()
    argenta = bot.Argenta()
    log = logging.getLogger()

    try:
        pool = loop.run_until_complete(db.create_pool(config.DATABASE_URL))
    except Exception as e:
        log.exception('Could not set up PostgreSQL. Exiting.')
        return

    loop.run_until_complete(db.create_tables(pool))
    argenta.pool = pool
    argenta.run()


def main():
    with setup_logging():
        run_bot()


if __name__ == "__main__":
    main()
