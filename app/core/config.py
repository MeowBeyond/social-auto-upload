import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.resolve()

# 简易解析 .env 文件（如果存在的话），不需要额外安装 python-dotenv
env_file = BASE_DIR / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                # setdefault 保证不会覆盖系统已有的真实环境变量
                os.environ.setdefault(key.strip(), val.strip(' "\''))

# 判断当前环境，默认为开发环境 dev，生产环境可设置为 prod
# 可以在终端通过 export ENV=prod 运行，或者写在 .env 文件里
ENV = os.environ.get("ENV", "dev")

# 公共配置
XHS_SERVER = os.environ.get("XHS_SERVER", "http://127.0.0.1:11901")
LOCAL_CHROME_PATH = os.environ.get("LOCAL_CHROME_PATH", "")

if ENV == "prod":
    # ================= 生产环境配置 =================
    LOCAL_CHROME_HEADLESS = os.environ.get("LOCAL_CHROME_HEADLESS", "True").lower() in ("true", "1", "t", "yes")
    DEBUG_MODE = os.environ.get("DEBUG_MODE", "False").lower() in ("true", "1", "t", "yes")

    # 生产数据库
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysqldc0d6bd7ec9f.rds.ivolces.com")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "wanling")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "fLdlC2fNdONGzVC7")
    MYSQL_DB = os.environ.get("MYSQL_DB", "ploymind")

else:
    # ================= 开发环境配置 =================
    LOCAL_CHROME_HEADLESS = os.environ.get("LOCAL_CHROME_HEADLESS", "False").lower() in ("true", "1", "t", "yes")
    DEBUG_MODE = os.environ.get("DEBUG_MODE", "True").lower() in ("true", "1", "t", "yes")

    # 开发数据库 (如果本地有数据库，可以将默认值改为 127.0.0.1)
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "rm-bp1bq6os2rt65n2sg0o.mysql.rds.aliyuncs.com")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "Z3uFf@rrn5Ghzyx")
    MYSQL_DB = os.environ.get("MYSQL_DB", "video_clips")
