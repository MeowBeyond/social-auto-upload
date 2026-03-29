from pathlib import Path

from app.core.config import BASE_DIR

Path(BASE_DIR / "cookies" / "tencent_uploader").mkdir(exist_ok=True)