from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLabel, QLineEdit,
    QDialogButtonBox, QFileDialog
)
from PyQt6.QtCore import Qt
import logging

from database.repositories.course_repository import CourseRepository
from models.course import Course

logger = logging.getLogger(__name__)


class CourseDialog(QDialog):
    """講座追加・編集ダイアログ"""
    
    def __init__(self, course: Course = None, parent=None):
        super().__init__(parent)
        self.course = course
        self.is_edit = course is not None
        
        self.init_ui()
        
        if self.is_edit:
            self.load_course_data()
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("講座編集" if self.is_edit else "講座追加")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 講座名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("講座名:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例: 数学I")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 備考1
        note1_layout = QHBoxLayout()
        note1_layout.addWidget(QLabel("備考1:"))
        self.note1_input = QLineEdit()
        self.note1_input.setPlaceholderText("例: 1年生")
        note1_layout.addWidget(self.note1_input)
        layout.addLayout(note1_layout)
        
        # 備考2
        note2_layout = QHBoxLayout()
        note2_layout.addWidget(QLabel("備考2:"))
        self.note2_input = QLineEdit()
        self.note2_input.setPlaceholderText("例: 必修")
        note2_layout.addWidget(self.note2_input)
        layout.addLayout(note2_layout)
        
        # 備考3
        note3_layout = QHBoxLayout()
        note3_layout.addWidget(QLabel("備考3:"))
        self.note3_input = QLineEdit()
        note3_layout.addWidget(self.note3_input)
        layout.addLayout(note3_layout)
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_course_data(self):
        """講座データを読み込む"""
        self.name_input.setText(self.course.course_name)
        if self.course.note1:
            self.note1_input.setText(self.course.note1)
        if self.course.note2:
            self.note2_input.setText(self.course.note2)
        if self.course.note3:
            self.note3_input.setText(self.course.note3)
    
    def get_course_data(self) -> Course:
        """入力された講座データを取得"""
        return Course(
            course_id=self.course.course_id if self.is_edit else None,
            course_name=self.name_input.text().strip(),
            note1=self.note1_input.text().strip() or None,
            note2=self.note2_input.text().strip() or None,
            note3=self.note3_input.text().strip() or None
        )
    
    def accept(self):
        """OK押下時の検証"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "入力エラー", "講座名を入力してください")
            return
        
        super().accept()


class CourseManagementView(QWidget):
    """講座管理ビュー"""
    
    def __init__(self, course_repo: CourseRepository, parent=None):
        super().__init__(parent)
        
        self.course_repo = course_repo
        self.courses = []
        
        self.init_ui()
        self.load_courses()
    
    def init_ui(self):
        """UI初期化"""
        layout = QVBoxLayout(self)
        
        # ツールバー
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("新規追加")
        add_btn.clicked.connect(self.add_course)
        toolbar.addWidget(add_btn)
        
        edit_btn = QPushButton("編集")
        edit_btn.clicked.connect(self.edit_course)
        toolbar.addWidget(edit_btn)
        
        delete_btn = QPushButton("削除")
        delete_btn.clicked.connect(self.delete_course)
        toolbar.addWidget(delete_btn)
        
        toolbar.addStretch()
        
        import_btn = QPushButton("CSVインポート")
        import_btn.clicked.connect(self.import_csv)
        toolbar.addWidget(import_btn)
        
        export_btn = QPushButton("CSVエクスポート")
        export_btn.clicked.connect(self.export_csv)
        toolbar.addWidget(export_btn)
        
        layout.addLayout(toolbar)
        
        # テーブル
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "講座名", "備考1", "備考2", "備考3"
        ])
        
        # ヘッダー設定
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # ダブルクリックで編集
        self.table.doubleClicked.connect(self.edit_course)
        
        layout.addWidget(self.table)
    
    def load_courses(self):
        """講座一覧を読み込む"""
        try:
            self.courses = self.course_repo.get_all_courses()
            self.update_table()
            logger.info(f"講座を読み込みました ({len(self.courses)}件)")
        except Exception as e:
            logger.error(f"講座読み込みエラー: {e}")
            QMessageBox.critical(
                self,
                "エラー",
                f"講座の読み込みに失敗しました:\n{str(e)}"
            )
    
    def update_table(self):
        """テーブルを更新"""
        self.table.setRowCount(len(self.courses))
        
        for row, course in enumerate(self.courses):
            self.table.setItem(row, 0, QTableWidgetItem(str(course.course_id)))
            self.table.setItem(row, 1, QTableWidgetItem(course.course_name))
            self.table.setItem(row, 2, QTableWidgetItem(course.note1 or ""))
            self.table.setItem(row, 3, QTableWidgetItem(course.note2 or ""))
            self.table.setItem(row, 4, QTableWidgetItem(course.note3 or ""))
    
    def add_course(self):
        """講座を追加"""
        dialog = CourseDialog(parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                course = dialog.get_course_data()
                self.course_repo.create_course(course)
                self.load_courses()
                
                QMessageBox.information(
                    self,
                    "成功",
                    f"講座「{course.course_name}」を追加しました"
                )
                logger.info(f"講座を追加しました: {course.course_name}")
            
            except Exception as e:
                logger.error(f"講座追加エラー: {e}")
                QMessageBox.critical(
                    self,
                    "エラー",
                    f"講座の追加に失敗しました:\n{str(e)}"
                )
    
    def edit_course(self):
        """講座を編集"""
        selected_row = self.table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "編集する講座を選択してください")
            return
        
        course = self.courses[selected_row]
        dialog = CourseDialog(course, parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                updated_course = dialog.get_course_data()
                self.course_repo.update_course(updated_course)
                self.load_courses()
                
                QMessageBox.information(
                    self,
                    "成功",
                    f"講座「{updated_course.course_name}」を更新しました"
                )
                logger.info(f"講座を更新しました: {updated_course.course_name}")
            
            except Exception as e:
                logger.error(f"講座更新エラー: {e}")
                QMessageBox.critical(
                    self,
                    "エラー",
                    f"講座の更新に失敗しました:\n{str(e)}"
                )
    
    def delete_course(self):
        """講座を削除"""
        selected_row = self.table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "削除する講座を選択してください")
            return
        
        course = self.courses[selected_row]
        
        reply = QMessageBox.question(
            self,
            "削除確認",
            f"講座「{course.course_name}」を削除しますか？\n"
            f"関連する生徒データと成績データも削除されます。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.course_repo.delete_course(course.course_id)
                self.load_courses()
                
                QMessageBox.information(
                    self,
                    "成功",
                    f"講座「{course.course_name}」を削除しました"
                )
                logger.info(f"講座を削除しました: {course.course_name}")
            
            except Exception as e:
                logger.error(f"講座削除エラー: {e}")
                QMessageBox.critical(
                    self,
                    "エラー",
                    f"講座の削除に失敗しました:\n{str(e)}"
                )
    
    def import_csv(self):
        """CSVインポート（差し替え式）"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "CSVファイルを選択",
            "",
            "CSVファイル (*.csv);;全てのファイル (*.*)"
        )
        
        if not file_path:
            return
        
        # 確認ダイアログ
        reply = QMessageBox.question(
            self,
            "差し替え確認",
            "CSVファイルから講座を一括インポート（差し替え）します。\n"
            "既存の全ての講座が削除され、CSVのデータで置き換えられます。\n"
            "関連する生徒データと成績データも削除されます。\n\n"
            "自動バックアップが作成されます。\n\n"
            "続行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            result = self.course_repo.import_from_csv_with_replacement(file_path)
            
            message = (
                f"インポートが完了しました:\n\n"
                f"削除: {result['deleted']}件\n"
                f"作成: {result['created']}件\n"
            )
            
            if result.get('backup_path'):
                message += f"\nバックアップ:\n{result['backup_path']}"
            
            if result['errors']:
                message += f"\n\nエラー: {len(result['errors'])}件\n"
                message += "\n".join(result['errors'][:5])
                if len(result['errors']) > 5:
                    message += f"\n... 他 {len(result['errors']) - 5}件"
            
            self.load_courses()
            
            QMessageBox.information(self, "インポート完了", message)
            logger.info(f"CSVインポート完了: {file_path}")
        
        except Exception as e:
            logger.error(f"CSVインポートエラー: {e}")
            QMessageBox.critical(
                self,
                "エラー",
                f"CSVインポートに失敗しました:\n{str(e)}"
            )

    def export_csv(self):
        """CSVエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "CSVファイルを保存",
            "courses.csv",
            "CSVファイル (*.csv);;全てのファイル (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            self.course_repo.export_to_csv(file_path)
            
            QMessageBox.information(
                self,
                "エクスポート完了",
                f"講座データをエクスポートしました:\n{file_path}"
            )
            logger.info(f"CSVエクスポート完了: {file_path}")
        
        except Exception as e:
            logger.error(f"CSVエクスポートエラー: {e}")
            QMessageBox.critical(
                self,
                "エラー",
                f"CSVエクスポートに失敗しました:\n{str(e)}"
            )