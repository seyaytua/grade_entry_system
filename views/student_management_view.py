from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLabel, QLineEdit,
    QDialogButtonBox, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt
import logging

from database.repositories.course_repository import CourseRepository
from database.repositories.student_repository import StudentRepository
from models.student import Student

logger = logging.getLogger(__name__)


class StudentDialog(QDialog):
    """生徒追加・編集ダイアログ"""
    
    def __init__(self, course_id: int, student: Student = None, parent=None):
        super().__init__(parent)
        self.course_id = course_id
        self.student = student
        self.is_edit = student is not None
        
        self.init_ui()
        
        if self.is_edit:
            self.load_student_data()
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("生徒編集" if self.is_edit else "生徒追加")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 生徒番号
        number_layout = QHBoxLayout()
        number_layout.addWidget(QLabel("生徒番号:"))
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("例: 001")
        number_layout.addWidget(self.number_input)
        layout.addLayout(number_layout)
        
        # クラス番号
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("クラス番号:"))
        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("例: 1-A")
        class_layout.addWidget(self.class_input)
        layout.addLayout(class_layout)
        
        # 生徒氏名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("生徒氏名:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例: 山田太郎")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 備考1
        note1_layout = QHBoxLayout()
        note1_layout.addWidget(QLabel("備考1:"))
        self.note1_input = QLineEdit()
        note1_layout.addWidget(self.note1_input)
        layout.addLayout(note1_layout)
        
        # 備考2
        note2_layout = QHBoxLayout()
        note2_layout.addWidget(QLabel("備考2:"))
        self.note2_input = QLineEdit()
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
    
    def load_student_data(self):
        """生徒データを読み込む"""
        self.number_input.setText(self.student.student_number)
        if self.student.class_number:
            self.class_input.setText(self.student.class_number)
        self.name_input.setText(self.student.student_name)
        if self.student.note1:
            self.note1_input.setText(self.student.note1)
        if self.student.note2:
            self.note2_input.setText(self.student.note2)
        if self.student.note3:
            self.note3_input.setText(self.student.note3)
    
    def get_student_data(self) -> Student:
        """入力された生徒データを取得"""
        return Student(
            id=self.student.id if self.is_edit else None,
            course_id=self.course_id,
            student_number=self.number_input.text().strip(),
            class_number=self.class_input.text().strip() or None,
            student_name=self.name_input.text().strip(),
            note1=self.note1_input.text().strip() or None,
            note2=self.note2_input.text().strip() or None,
            note3=self.note3_input.text().strip() or None
        )
    
    def accept(self):
        """OK押下時の検証"""
        if not self.number_input.text().strip():
            QMessageBox.warning(self, "入力エラー", "生徒番号を入力してください")
            return
        
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "入力エラー", "生徒氏名を入力してください")
            return
        
        super().accept()


class StudentManagementView(QWidget):
    """生徒名簿管理ビュー"""
    
    def __init__(self, course_repo: CourseRepository,
                 student_repo: StudentRepository, parent=None):
        super().__init__(parent)
        
        self.course_repo = course_repo
        self.student_repo = student_repo
        self.students = []
        self.current_course_id = None
        
        self.init_ui()
        self.refresh_courses()
    
    def init_ui(self):
        """UI初期化"""
        layout = QVBoxLayout(self)
        
        # 講座選択
        course_layout = QHBoxLayout()
        course_layout.addWidget(QLabel("講座:"))
        
        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(self.on_course_changed)
        course_layout.addWidget(self.course_combo, 1)
        
        layout.addLayout(course_layout)
        
        # ツールバー
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("新規追加")
        add_btn.clicked.connect(self.add_student)
        toolbar.addWidget(add_btn)
        
        edit_btn = QPushButton("編集")
        edit_btn.clicked.connect(self.edit_student)
        toolbar.addWidget(edit_btn)
        
        delete_btn = QPushButton("削除")
        delete_btn.clicked.connect(self.delete_student)
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "生徒番号", "クラス", "氏名", "備考1", "備考2", "備考3"
        ])
        
        # ヘッダー設定
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # ダブルクリックで編集
        self.table.doubleClicked.connect(self.edit_student)
        
        layout.addWidget(self.table)
    
    def refresh_courses(self):
        """講座リストを更新"""
        try:
            self.course_combo.clear()
            courses = self.course_repo.get_all_courses()
            
            for course in courses:
                self.course_combo.addItem(course.course_name, course.course_id)
            
            logger.debug(f"講座リストを更新しました ({len(courses)}件)")
        except Exception as e:
            logger.error(f"講座リスト更新エラー: {e}")
            QMessageBox.critical(
                self,
                "エラー",
                f"講座リストの更新に失敗しました:\n{str(e)}"
            )
    
    def on_course_changed(self):
        """講座変更時の処理"""
        self.current_course_id = self.course_combo.currentData()
        if self.current_course_id:
            self.load_students()
    
    def load_students(self):
        """生徒一覧を読み込む"""
        if not self.current_course_id:
            return
        
        try:
            self.students = self.student_repo.get_students_by_course(
                self.current_course_id
            )
            self.update_table()
            logger.info(f"生徒を読み込みました ({len(self.students)}名)")
        except Exception as e:
            logger.error(f"生徒読み込みエラー: {e}")
            QMessageBox.critical(
                self,
                "エラー",
                f"生徒の読み込みに失敗しました:\n{str(e)}"
            )
    
    def update_table(self):
        """テーブルを更新"""
        self.table.setRowCount(len(self.students))
        
        for row, student in enumerate(self.students):
            self.table.setItem(row, 0, QTableWidgetItem(student.student_number))
            self.table.setItem(row, 1, QTableWidgetItem(student.class_number or ""))
            self.table.setItem(row, 2, QTableWidgetItem(student.student_name))
            self.table.setItem(row, 3, QTableWidgetItem(student.note1 or ""))
            self.table.setItem(row, 4, QTableWidgetItem(student.note2 or ""))
            self.table.setItem(row, 5, QTableWidgetItem(student.note3 or ""))
    
    def add_student(self):
        """生徒を追加"""
        if not self.current_course_id:
            QMessageBox.warning(self, "警告", "講座を選択してください")
            return
        
        dialog = StudentDialog(self.current_course_id, parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                student = dialog.get_student_data()
                self.student_repo.create_student(student)
                self.load_students()
                
                QMessageBox.information(
                    self,
                    "成功",
                    f"生徒「{student.student_name}」を追加しました"
                )
                logger.info(f"生徒を追加しました: {student.student_name}")
            
            except Exception as e:
                logger.error(f"生徒追加エラー: {e}")
                QMessageBox.critical(
                    self,
                    "エラー",
                    f"生徒の追加に失敗しました:\n{str(e)}"
                )
    
    def edit_student(self):
        """生徒を編集"""
        selected_row = self.table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "編集する生徒を選択してください")
            return
        
        student = self.students[selected_row]
        dialog = StudentDialog(self.current_course_id, student, parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                updated_student = dialog.get_student_data()
                self.student_repo.update_student(updated_student)
                self.load_students()
                
                QMessageBox.information(
                    self,
                    "成功",
                    f"生徒「{updated_student.student_name}」を更新しました"
                )
                logger.info(f"生徒を更新しました: {updated_student.student_name}")
            
            except Exception as e:
                logger.error(f"生徒更新エラー: {e}")
                QMessageBox.critical(
                    self,
                    "エラー",
                    f"生徒の更新に失敗しました:\n{str(e)}"
                )
    
    def delete_student(self):
        """生徒を削除"""
        selected_row = self.table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "削除する生徒を選択してください")
            return
        
        student = self.students[selected_row]
        
        reply = QMessageBox.question(
            self,
            "削除確認",
            f"生徒「{student.student_name}」を削除しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.student_repo.delete_student(student.id)
                self.load_students()
                
                QMessageBox.information(
                    self,
                    "成功",
                    f"生徒「{student.student_name}」を削除しました"
                )
                logger.info(f"生徒を削除しました: {student.student_name}")
            
            except Exception as e:
                logger.error(f"生徒削除エラー: {e}")
                QMessageBox.critical(
                    self,
                    "エラー",
                    f"生徒の削除に失敗しました:\n{str(e)}"
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
        if self.current_course_id:
            course = self.course_repo.get_course_by_id(self.current_course_id)
            course_name = course.course_name if course else "選択中の講座"
            message = (
                f"CSVファイルから生徒を一括インポート（差し替え）します。\n"
                f"講座「{course_name}」の既存の全ての生徒が削除され、\n"
                f"CSVのデータで置き換えられます。\n\n"
                f"自動バックアップが作成されます。\n\n"
                f"続行しますか？"
            )
        else:
            message = (
                f"CSVファイルから生徒を一括インポート（差し替え）します。\n"
                f"全ての講座の既存の生徒が削除され、\n"
                f"CSVのデータで置き換えられます。\n\n"
                f"自動バックアップが作成されます。\n\n"
                f"続行しますか？"
            )
        
        reply = QMessageBox.question(
            self,
            "差し替え確認",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            result = self.student_repo.import_from_csv_with_replacement(
                file_path, 
                self.current_course_id
            )
            
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
            
            self.load_students()
            
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
            "students.csv",
            "CSVファイル (*.csv);;全てのファイル (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            self.student_repo.export_to_csv(file_path, self.current_course_id)
            
            QMessageBox.information(
                self,
                "エクスポート完了",
                f"生徒データをエクスポートしました:\n{file_path}"
            )
            logger.info(f"CSVエクスポート完了: {file_path}")
        
        except Exception as e:
            logger.error(f"CSVエクスポートエラー: {e}")
            QMessageBox.critical(
                self,
                "エラー",
                f"CSVエクスポートに失敗しました:\n{str(e)}"
            )