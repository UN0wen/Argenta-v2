import logging
import bot


def setup_logging():
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


def main():
    argenta = bot.Argenta()
    setup_logging()
    argenta.run()


if __name__ == "__main__":
    main()
