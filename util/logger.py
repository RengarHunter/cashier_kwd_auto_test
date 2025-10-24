import inspect
from loguru import logger
from config.conf import cm  # 你的配置实例


class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def log(self, level, message):
        frame_records = inspect.stack()[1]
        caller_file = frame_records[1]
        caller_line = frame_records[2]
        # ---------------- 关键修改：添加 raw=True，禁止Loguru解析消息中的{} ----------------
        logger.opt(depth=1, exception=None, raw=True).log(
            level.upper(), 
            message,  # 消息会被当作纯字符串，不解析{}
            file=caller_file, 
            line=caller_line
        )


def custom_formatter(record):
    levelname = record["level"].name
    asctime = record["time"].strftime("%Y-%m-%d %H:%M:%S")
    filename = record["file"]
    lineno = record["line"]
    message = record["message"]
    return f"{levelname}\t{asctime}\t[{filename}:{lineno}]\t{message}\n"


logger.remove()  # 移除默认logger
log_file_path = cm.log_file
logger.add(log_file_path, format=custom_formatter, level="DEBUG")

# 全局日志实例
logger_instance = Logger()