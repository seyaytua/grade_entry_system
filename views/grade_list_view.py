from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QComboBox, QDateEdit,
    QLabel, QLineEdit, QGroupBox, QDialog, QDialogButtonBox,
    QTextEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
import logging
from pathlib import Path

from database.repositories.course_repository import CourseRepository
from database.repositories.grade_repository import GradeRepository

logger = logging.getLogger(__name__)


class ImportPreviewDialog(QDialog):
    """インポートプレビューダイアログ"""
    
    def __init__(self, csv_path: str, filters: dict, 
                 existing_count: int, new_count: int, parent=None):
        super().__init__(parent)
        self.csv_path = csv_path
        self.filters = filters
        self.existing_count = existing_count
        self.new_count = new_count
        
        self.init_ui()
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("インポートプレビュー")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # ファイル情報
        file_label = QLabel(f"ファイル: {Path(self.csv_path).name}")
        file_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(file_label)
        
        layout.addWidget(QLabel(""))
        
        # フィルタ情報
        filter_group = QGroupBox("差し替え範囲")
        filter_layout = QVBoxLayout(filter_group)
        
        if self.filters.get('course_ids'):
            course_text = f"講座ID: {', '.join(map(str, self.filters['course_ids']))}"
        else:
            course_text = "講座: 全て"
        filter_layout.addWidget(QLabel(course_text))
        
        date_text = f"期間: {self.filters.get('start_date', '全て')} 〜 {self.filters.get('end_date', '全て')}"
        filter_layout.addWidget(QLabel(date_text))
        
        layout.addWidget(filter_group)
        
        layout.addWidget(QLabel(""))
        
        # プレビュー情報
        preview_group = QGroupBox("実行内容")
        preview_layout = QVBoxLayout(preview_group)
        
        delete_label = QLabel(f"削除: {self.existing_count}件")
        delete_label.setStyleSheet("color: red; font-size: 14pt; font-weight: bold;")
        preview_layout.addWidget(delete_label)
        
        add_label = QLabel(f"追加: {self.new_count}件")
        add_label.setStyleSheet("color: green; font-size: 14pt; font-weight: bold;")
        preview_layout.addWidget(add_label)
        
        diff = self.new_count - self.existing_count
        diff_text = f"差分: {diff:+d}件"
        diff_label = QLabel(diff_text)
        diff_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        preview_layout.addWidget(diff_label)
        
        layout.addWidget(preview_group)
        
        layout.addWidget(QLabel(""))
        
        # 警告メッセージ
        warning_text = QTextEdit()
        warning_text.setReadOnly(True)
        warning_text.setMaximumHeight(100)
        
        warning_msg = "⚠️ 重要な注意事項:\n\n"
        warning_msg += "• 指定範囲の既存データは全て削除されます\n"
        warning_msg += "• CSVのデータで完全に置き換えられます\n"
        warning_msg += "• 自動バックアップが作成されます\n"
        
        if self.existing_count >= 100:
            warning_msg += f"\n⚠️ 大量のデータ（{self.existing_count}件）を削除します！"
        
        warning_text.setPlainText(warning_msg)
        warning_text.setStyleSheet("background-color: #FFF3CD; border: 1px solid #FFC107;")
        layout.addWidget(warning_text)
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("インポート実行")
        ok_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 5px 15px;")
        
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("キャンセル")
        
        layout.addWidget(button_box)


class GradeListView(QWidget):
    """成績一覧表ビュー"""
    
    def __init__(self, course_repo: CourseRepository,
                 grade_repo: GradeRepository, parent=None):
        super().__init__(parent)
        
        self.course_repo = course_repo
        self.grade_repo = grade_repo
        self.grade_list = []
        
        self.init_ui()
        self.refresh_courses()
    
    def init_ui(self):
        """UI初期化"""
        layout = QVBoxLayout(self)
        
        # フィルタエリア
        filter_group = QGroupBox("フィルタ条件")
        filter_layout = QVBoxLayout(filter_group)
        
        # 講座選択
        course_layout = QHBoxLayout()
        course_layout.addWidget(QLabel("講座:"))
        self.course_combo = QComboBox()
        self.course_combo.addItem("全て", None)
        course_layout.addWidget(self.course_combo, 1)
        filter_layout.addLayout(course_layout)
        
        # 期間指定
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("期間:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("〜"))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        
        date_layout.addStretch()
        filter_layout.addLayout(date_layout)
        
        # 生徒番号・クラス
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("生徒番号:"))
        self.student_number_input = QLineEdit()
        self.student_number_input.setPlaceholderText("部分一致")
        search_layout.addWidget(self.student_number_input)
        
        search_layout.addWidget(QLabel("クラス:"))
        self.class_number_input = QLineEdit()
        self.class_number_input.setPlaceholderText("例: 1-A")
        search_layout.addWidget(self.class_number_input)
        
        search_layout.addStretch()
        filter_layout.addLayout(search_layout)
        
        # フィルタボタン
        filter_btn_layout = QHBoxLayout()
        filter_btn_layout.addStretch()
        
        apply_btn = QPushButton("フィルタ適用")
        apply_btn.clicked.connect(self.apply_filters)
        filter_btn_layout.addWidget(apply_btn)
        
        clear_btn = QPushButton("フィルタクリア")
        clear_btn.clicked.connect(self.clear_filters)
        filter_btn_layout.addWidget(clear_btn)
        
        filter_layout.addLayout(filter_btn_layout)
        
        layout.addWidget(filter_group)
        
        # ツールバー
        toolbar = QHBoxLayout()
        
        export_btn = QPushButton("CSVエクスポート")
        export_btn.clicked.connect(self.export_csv)
        toolbar.addWidget(export_btn)
        
        import_btn = QPushButton("CSV一括インポート（差し替え）")
        import_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        import_btn.clicked.connect(self.import_csv)
        toolbar.addWidget(import_btn)
        
        toolbar.addStretch()
        
        delete_btn = QPushButton("削除")
        delete_btn.clicked.connect(self.delete_grade)
        toolbar.addWidget(delete_btn)
        
        layout.addLayout(toolbar)
        
        # テーブル
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "講座名", "授業日", "生徒番号", "氏名", "クラス",
            "成績1", "成績2", "成績3", "成績4", "成績5", "成績6",
            "備考1", "備考2"
        ])
        
        # ヘッダー設定（全ての列を自由に変更可能に）
        header = self.table.horizontalHeader()
        for i in range(13):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        
        # 初期の列幅を設定
        self.table.setColumnWidth(0, 150)  # 講座名
        self.table.setColumnWidth(1, 100)  # 授業日
        self.table.setColumnWidth(2, 80)   # 生徒番号
        self.table.setColumnWidth(3, 120)  # 氏名
        self.table.setColumnWidth(4, 80)   # クラス
        self.table.setColumnWidth(5, 60)   # 成績1
        self.table.setColumnWidth(6, 60)   # 成績2
        self.table.setColumnWidth(7, 60)   # 成績3
        self.table.setColumnWidth(8, 60)   # 成績4
        self.table.setColumnWidth(9, 60)   # 成績5
        self.table.setColumnWidth(10, 60)  # 成績6
        self.table.setColumnWidth(11, 150) # 備考1
        self.table.setColumnWidth(12, 150) # 備考2
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)
        
        # 件数表示
        self.count_label = QLabel("0件")
        layout.addWidget(self.count_label)
    
    def refresh_courses(self):
        """講座リストを更新"""
        try:
            self.course_combo.clear()
            self.course_combo.addItem("全て", None)
            
            courses = self.course_repo.get_all_courses()
            for course in courses:
                self.course_combo.addItem(course.course_name, course.course_id)
            
            logger.debug(f"講座リストを更新しました ({len(courses)}件)")
        except Exception as e:
            logger.error(f"講座リスト更新エラー: {e}")
            QMessageBox.critical(self, "エラー", f"講座リストの更新に失敗しました:\n{str(e)}")
    
    def get_filter_params(self):
        """フィルタパラメータを取得"""
        filters = {}
        
        course_id = self.course_combo.currentData()
        if course_id:
            filters['course_ids'] = [course_id]
        
        filters['start_date'] = self.start_date.date().toString("yyyy-MM-dd")
        filters['end_date'] = self.end_date.date().toString("yyyy-MM-dd")
        
        student_number = self.student_number_input.text().strip()
        if student_number:
            filters['student_number'] = student_number
        
        class_number = self.class_number_input.text().strip()
        if class_number:
            filters['class_number'] = class_number
        
        return filters
    
    def apply_filters(self):
        """フィルタを適用"""
        try:
            filters = self.get_filter_params()
            self.grade_list = self.grade_repo.get_grade_list(filters)
            self.update_table()
            logger.info(f"成績一覧を取得しました ({len(self.grade_list)}件)")
        except Exception as e:
            logger.error(f"成績一覧取得エラー: {e}")
            QMessageBox.critical(self, "エラー", f"成績一覧の取得に失敗しました:\n{str(e)}")
    
    def clear_filters(self):
        """フィルタをクリア"""
        self.course_combo.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date.setDate(QDate.currentDate())
        self.student_number_input.clear()
        self.class_number_input.clear()
        self.grade_list = []
        self.update_table()
    
    def update_table(self):
        """テーブルを更新"""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.grade_list))
        
        for row, grade in enumerate(self.grade_list):
            # 各列のデータを文字列に変換してセット
            self.table.setItem(row, 0, QTableWidgetItem(str(grade.course_name)))
            self.table.setItem(row, 1, QTableWidgetItem(str(grade.entry_date)))
            self.table.setItem(row, 2, QTableWidgetItem(str(grade.student_number)))
            self.table.setItem(row, 3, QTableWidgetItem(str(grade.student_name)))
            self.table.setItem(row, 4, QTableWidgetItem(str(grade.class_number) if grade.class_number else ""))
            
            # 成績データ（None の場合は空文字列）
            for i, attr in enumerate(['grade1', 'grade2', 'grade3', 'grade4', 'grade5', 'grade6'], 5):
                val = getattr(grade, attr)
                self.table.setItem(row, i, QTableWidgetItem(str(val) if val is not None else ""))
            
            # 備考
            self.table.setItem(row, 11, QTableWidgetItem(str(grade.note1) if grade.note1 else ""))
            self.table.setItem(row, 12, QTableWidgetItem(str(grade.note2) if grade.note2 else ""))
        
        self.table.setSortingEnabled(True)
        self.count_label.setText(f"{len(self.grade_list)}件")
    
    def delete_grade(self):
        """成績を削除"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "削除する成績を選択してください")
            return
        
        grade = self.grade_list[selected_row]
        reply = QMessageBox.question(
            self, "削除確認",
            f"以下の成績を削除しますか?\n\n講座: {grade.course_name}\n日付: {grade.entry_date}\n生徒: {grade.student_name}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.grade_repo.delete_grade(grade.id)
                self.apply_filters()
                QMessageBox.information(self, "成功", "成績を削除しました")
            except Exception as e:
                logger.error(f"成績削除エラー: {e}")
                QMessageBox.critical(self, "エラー", f"成績の削除に失敗しました:\n{str(e)}")
    
    def export_csv(self):
        """CSVエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(self, "CSVファイルを保存", "grades.csv", "CSVファイル (*.csv)")
        if not file_path:
            return
        
        try:
            filters = self.get_filter_params()
            self.grade_repo.export_to_csv(file_path, filters)
            QMessageBox.information(self, "エクスポート完了", f"成績データをエクスポートしました:\n{file_path}")
        except Exception as e:
            logger.error(f"CSVエクスポートエラー: {e}")
            QMessageBox.critical(self, "エラー", f"CSVエクスポートに失敗しました:\n{str(e)}")
    
    def import_csv(self):
        """CSV一括インポート（差し替え式）"""
        file_path, _ = QFileDialog.getOpenFileName(self, "CSVファイルを選択", "", "CSVファイル (*.csv)")
        if not file_path:
            return
        
        try:
            # 現在のフィルタ条件を取得
            filters = self.get_filter_params()
            
            # プレビュー計算
            existing_grades = self.grade_repo.get_grade_list(filters)
            existing_count = len(existing_grades)
            
            # CSVの件数を取得
            import csv
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                new_count = sum(1 for _ in reader)
            
            # プレビューダイアログ表示
            dialog = ImportPreviewDialog(file_path, filters, existing_count, new_count, self)
            
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            
            # インポート実行
            result = self.grade_repo.import_from_csv_with_replacement(file_path, filters)
            
            # 結果表示
            message = f"インポートが完了しました:\n\n"
            message += f"削除: {result['deleted']}件\n"
            message += f"追加: {result['created']}件\n"
            
            if result.get('backup_path'):
                message += f"\nバックアップ:\n{result['backup_path']}"
            
            if result['errors']:
                message += f"\n\nエラー: {len(result['errors'])}件\n"
                message += "\n".join(result['errors'][:5])
                if len(result['errors']) > 5:
                    message += f"\n... 他 {len(result['errors']) - 5}件"
            
            self.apply_filters()
            QMessageBox.information(self, "インポート完了", message)
            
        except Exception as e:
            logger.error(f"CSVインポートエラー: {e}")
            QMessageBox.critical(self, "エラー", f"CSVインポートに失敗しました:\n{str(e)}")
