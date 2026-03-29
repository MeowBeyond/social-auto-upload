import pymysql
import pymysql.cursors
from contextlib import contextmanager
from app.core.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

@contextmanager
def get_db(dict_cursor=True):
    cursor_cls = pymysql.cursors.DictCursor if dict_cursor else pymysql.cursors.Cursor
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset='utf8mb4',
        cursorclass=cursor_cls,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
