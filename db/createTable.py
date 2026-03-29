import pymysql
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.core.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

conn = pymysql.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    charset='utf8mb4',
)
cursor = conn.cursor()

cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
cursor.execute(f"USE `{MYSQL_DB}`")

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_info (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type INT NOT NULL,
    filePath VARCHAR(512) NOT NULL,
    userName VARCHAR(255) NOT NULL,
    status INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS file_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(512) NOT NULL,
    filesize DOUBLE,
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(512)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
''')

conn.commit()
print("✅ MySQL 数据库和表创建成功")
conn.close()
