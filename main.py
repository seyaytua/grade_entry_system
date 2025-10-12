#!/usr/bin/env python3
"""成績入力システム メインエントリーポイント"""

import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加（main.pyの親ディレクトリ）
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'grade_entry_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from views.main_window import MainWindow


def main():
    """アプリケーションメイン関数"""
    logger.info("=" * 60)
    logger.info("成績入力システム起動")
    logger.info("=" * 60)
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("成績入力システム")
        app.setOrganizationName("GradeEntrySystem")
        
        # メインウィンドウ作成
        window = MainWindow()
        window.show()
        
        logger.info("メインウィンドウを表示しました")
        
        # イベントループ開始
        sys.exit(app.exec())
    
    except Exception as e:
        logger.error(f"アプリケーション起動エラー: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
