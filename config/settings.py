"""アプリケーション設定"""

# アプリケーション情報
APP_NAME = "成績入力システム"
APP_VERSION = "1.0.0"
ORGANIZATION = "GradeEntrySystem"

# データベース設定
DB_PATH = "data/database.db"
BACKUP_DIR = "data/backups"

# ウィンドウ設定
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 700

# 画像プレビュー設定
IMAGE_ZOOM_FACTOR = 1.1
IMAGE_MIN_ZOOM = 0.1
IMAGE_MAX_ZOOM = 5.0

# 成績設定
GRADE_RADIO_OPTIONS = [
    (0, "0"),
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4")
]

# ファイル設定
SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg", ".pdf"]
CSV_ENCODING = "utf-8-sig"

# ログ設定
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
