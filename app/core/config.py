from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.resolve()
XHS_SERVER = "http://127.0.0.1:11901"  # only used by xhs-related flows
LOCAL_CHROME_PATH = ""  # optional, e.g. C:/Program Files/Google/Chrome/Application/chrome.exe
LOCAL_CHROME_HEADLESS = False  # default headless behavior for uploader/examples
DEBUG_MODE = True  # default debug behavior

# MySQL Configuration
MYSQL_HOST = 'rm-bp1bq6os2rt65n2sg0o.mysql.rds.aliyuncs.com'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Z3uFf@rrn5Ghzyx'
MYSQL_DB = 'video_clips'
