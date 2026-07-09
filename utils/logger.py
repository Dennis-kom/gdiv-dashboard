import logging
import colorlog
from data.internal.configurations import DebugConfig
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s-%(levelname)s-%(message)s",
#     datefmt="%m/%d-%H:%M:%S"
# )




def color_logger():
    # יצירת לוגר ייחודי לפרויקט שלך
    logger = logging.getLogger("gdiv_dashboard")

    # מניעת כפילויות של הנדלרים אם הפונקציה נקראת שוב
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # 1. הגדרת הצבעים לכל רמת לוג
        log_colors = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        # 2. יצירת הפורמטר הצבעוני (שים לב ל-log_color בתחילת הפורמט)
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors=log_colors
        )

        # 3. הגדרת הנדלר שידפיס לטרמינל (Console)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def log_pref(locations= None, message = None):
    setter = ""
    if locations:
        for key, itm in locations.items():
            setter += f"{key}-{itm}, "

    return f"{setter} | {message}"


def tracer(msg):
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    ORANGE = '\033[33m'
    if DebugConfig.tracer_active:
        print(f"{ORANGE}TRACE --> {msg}{RESET}")

def tracer_status(msg):
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    if DebugConfig.tracer_active:
        print(f"{RED}STATUS :: << {msg} >>{RESET}")
