import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMessageBox, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import logging

from config.settings import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
)
from database.db_manager import DatabaseManager
from database.repositories.course_repository import CourseRepository
from database.repositories.student_repository import StudentRepository
from database.repositories.grade_repository import GradeRepository
from views.grade_entry_view import GradeEntryView
from views.course_management_view import CourseManagementView
from views.student_management_view import StudentManagementView
from views.grade_list_view import GradeListView

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.db = None
        self.course_repo = None
        self.student_repo = None
        self.grade_repo = None
        
        self.init_database()
        self.init_ui()
    
    def init_database(self):
        """データベース初期化"""
        try:
            self.db = DatabaseManager()
            self.course_repo = CourseRepository(self.db)
            self.student_repo = StudentRepository(self.db)
            self.grade_repo = GradeRepository(self.db)
            logger.info("データベースを初期化しました")
        except Exception as e:
            logger.error(f"データベース初期化エラー: {e}")
            QMessageBox.critical(self, "エラー", f"データベースの初期化に失敗しました:\n{str(e)}")
            sys.exit(1)
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        self.create_menu_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        self.grade_entry_view = GradeEntryView(self.course_repo, self.student_repo, self.grade_repo)
        self.course_management_view = CourseManagementView(self.course_repo)
        self.student_management_view = StudentManagementView(self.course_repo, self.student_repo)
        self.grade_list_view = GradeListView(self.course_repo, self.grade_repo)
        
        self.tab_widget.addTab(self.grade_entry_view, "成績入力")
        self.tab_widget.addTab(self.course_management_view, "講座管理")
        self.tab_widget.addTab(self.student_management_view, "生徒名簿管理")
        self.tab_widget.addTab(self.grade_list_view, "成績一覧表")
        
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        logger.info("UIを初期化しました")
    
    def create_menu_bar(self):
        """メニューバー作成"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("ファイル(&F)")
        
        backup_action = QAction("データベースバックアップ(&B)", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("ヘルプ(&H)")
        
        about_action = QAction("バージョン情報(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def on_tab_changed(self, index):
        """タブ変更時の処理"""
        if index == 0:
            self.grade_entry_view.refresh_courses()
        elif index == 1:
            self.course_management_view.load_courses()
        elif index == 2:
            self.student_management_view.refresh_courses()
        elif index == 3:
            self.grade_list_view.refresh_courses()
    
    def backup_database(self):
        """データベースバックアップ"""
        try:
            backup_path = self.db.backup_database()
            QMessageBox.information(self, "バックアップ完了", f"データベースをバックアップしました:\n{backup_path}")
        except Exception as e:
            logger.error(f"バックアップエラー: {e}")
            QMessageBox.critical(self, "エラー", f"バックアップに失敗しました:\n{str(e)}")
    
    def show_about(self):
        """バージョン情報表示"""
        QMessageBox.about(
            self, f"{APP_NAME}について",
            f"<h2>{APP_NAME}</h2><p>バージョン: {APP_VERSION}</p>"
            f"<p>スキャンされた資料を参照しながら、<br>効率的に学生の成績を入力・管理するシステムです。</p>"
        )
    
    def closeEvent(self, event):
        """ウィンドウクローズイベント"""
        reply = QMessageBox.question(
            self, "終了確認", "アプリケーションを終了しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db:
                self.db.close()
            logger.info("アプリケーションを終了しました")
            event.accept()
        else:
            event.ignore()
