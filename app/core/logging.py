from loguru import logger
import sys
import os
from typing import Union
import logging

def configure_logger(
    enable_json_logs: bool = False,
    enable_sql_logs: bool = False,
    level: Union[int, str] = "INFO",
    log_file: str = "logs/app.log",
) -> None:
    """
    Настройка логирования с использованием Loguru.

    :param enable_json_logs: Включить JSON-форматирование логов.
    :param enable_sql_logs: Включить логирование SQLAlchemy.
    :param level: Уровень логирования (например, "INFO", "DEBUG").
    :param log_file: Путь к файлу логов.
    """

    # Удаляем стандартный обработчик Loguru, чтобы избежать дублирования
    logger.remove()

    # Создаем директорию для логов, если она не существует
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    if enable_json_logs:
        # Добавляем JSON-форматирование
        logger.add(
            sys.stdout,
            format="{\"time\": \"{time:YYYY-MM-DD HH:mm:ss}\", \"level\": \"{level}\", \"message\": \"{message}\"}",
            level=level,
            serialize=True,
        )
        logger.add(
            log_file,
            format="{\"time\": \"{time:YYYY-MM-DD HH:mm:ss}\", \"level\": \"{level}\", \"message\": \"{message}\"}",
            level=level,
            rotation="10 MB",
            serialize=True,
        )
    else:
        # Добавляем стандартное форматирование для консоли
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=level,
            colorize=True,
        )
        # Добавляем файл логов с ротацией
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            level=level,
            rotation="10 MB",
            retention="10 days",
            compression="zip",
        )

    # Настройка логирования для SQLAlchemy
    if not enable_sql_logs:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    # Настройка логирования для стандартных библиотек
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            level = logger.level(record.levelname).name if record.levelname in logger._levels else record.levelno
            frame, depth = sys._getframe(6), 6
            logger.opt(depth=depth, frame=frame).log(level, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=0)
