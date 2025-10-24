import inspect
from loguru import logger
from config.conf import cm


class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def log(self, level, message):
        # 1. 这两行获取调用栈信息，但只是为了兼容旧逻辑（实际Loguru会自动获取，可保留也可删除）
        frame_records = inspect.stack()[1]
        caller_file = frame_records[1]
        caller_line = frame_records[2]

        # 2. 关键修正：删除 `file=caller_file, line=caller_line` 这两个参数！
        # 只传 level.upper() 和 message，不传递任何额外kwargs
        logger.opt(depth=1, exception=None, raw=True).log(
            level.upper(),
            message  # 这里只传消息，没有其他参数！
        )


def custom_formatter(record):
    levelname = record["level"].name
    asctime = record["time"].strftime("%Y-%m-%d %H:%M:%S")
    # Loguru自动获取的文件和行号，无需手动传
    filename = record["file"].name
    lineno = record["line"]
    message = record["message"]
    return f"{levelname}\t{asctime}\t[{filename}:{lineno}]\t{message}\n"


logger.remove()
log_file_path = cm.log_file
logger.add(log_file_path, format=custom_formatter, level="DEBUG", encoding="utf-8")

logger_instance = Logger()