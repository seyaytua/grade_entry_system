"""PDF分割作業ビュー"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSplitter, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
from pathlib import Path
from typing import List, Dict

from models.student import Student
from models.grade import Grade
from models.course import Course
from models.split import SplitSettings, StudentPageAssignment, SplitResult
from views.widgets.image_preview_widget import ImagePreviewWidget
from views.widgets.student_assignment_item import StudentAssignmentItem
from utils.pdf_splitter import PDFSplitter

logger = logging.getLogger(__name__)


class PDFSplitView(QWidget):
    """PDF分割作業ビュー"""
    
    # シグナル
    split_completed = pyqtSignal(SplitResult)  # 分割完了
    cancelled = pyqtSignal()  # キャンセル
    
    def __init__(self, pdf_path: str, students: List[Student], 
                 grades: Dict[str, Grade], course: Course,
                 settings: SplitSettings, parent=None):
        super().__init__(parent)
        
        self.pdf_path = pdf_path
        self.students = students
        self.grades = grades  # {student_number: Grade}
        self.course = course
        self.settings = settings
        
        self.assignments: List[StudentPageAssignment] = []
        self.total_pages = 0
        
        # ウィジェット
        self.preview_widget: ImagePreviewWidget
        self.student_list_widget: QListWidget
        self.summary_label: QLabel
        self.page_label: QLabel
        
        self.init_ui()
        self.init_assignments()
        self.load_pdf()
    
    def init_ui(self):
        """UI初期化"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # ヘッダー
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("← 成績入力に戻る")
        back_btn.clicked.connect(self.on_cancel)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        
        title_label = QLabel("📄 PDF分割作業")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        execute_btn = QPushButton("✓ 分割実行")
        execute_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; "
            "font-weight: bold; font-size: 14pt; padding: 10px;"
        )
        execute_btn.clicked.connect(self.execute_split)
        header_layout.addWidget(execute_btn)
        
        layout.addLayout(header_layout)
        
        # メインエリア（左右分割）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左側: PDFプレビュー
        preview_panel = self.create_preview_panel()
        splitter.addWidget(preview_panel)
        
        # 右側: 生徒リスト
        student_panel = self.create_student_panel()
        splitter.addWidget(student_panel)
        
        # 分割比率 6:4
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        
        layout.addWidget(splitter)
    
    def create_preview_panel(self) -> QWidget:
        """プレビューパネル作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ヘッダー
        header = QLabel("📄 PDFプレビュー")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # プレビュー
        self.preview_widget = ImagePreviewWidget()
        layout.addWidget(self.preview_widget)
        
        # ページコントロール
        control_layout = QHBoxLayout()
        
        prev_btn = QPushButton("◀ 前")
        prev_btn.clicked.connect(self.preview_widget.prev_page)
        control_layout.addWidget(prev_btn)
        
        self.page_label = QLabel("1 / 1")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setMinimumWidth(100)
        control_layout.addWidget(self.page_label)
        
        next_btn = QPushButton("次 ▶")
        next_btn.clicked.connect(self.preview_widget.next_page)
        control_layout.addWidget(next_btn)
        
        layout.addLayout(control_layout)
        
        # ズームコントロール
        zoom_layout = QHBoxLayout()
        
        zoom_out_btn = QPushButton("縮小")
        zoom_out_btn.clicked.connect(self.preview_widget.zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        zoom_in_btn = QPushButton("拡大")
        zoom_in_btn.clicked.connect(self.preview_widget.zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        reset_btn = QPushButton("リセット")
        reset_btn.clicked.connect(self.preview_widget.reset_zoom)
        zoom_layout.addWidget(reset_btn)
        
        layout.addLayout(zoom_layout)
        
        return widget
    
    def create_student_panel(self) -> QWidget:
        """生徒パネル作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ヘッダー
        header = QLabel("👥 生徒リスト")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # サマリー
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet(
            "background-color: #E3F2FD; padding: 10px; "
            "border: 1px solid #2196F3; border-radius: 5px;"
        )
        layout.addWidget(self.summary_label)
        
        # 説明
        info_label = QLabel(
            "💡 ヒント:\n"
            "・生徒をクリックでプレビュー表示\n"
            "・ドラッグ&ドロップで順番変更\n"
            "・欠席チェックでスキップ"
        )
        info_label.setStyleSheet(
            "background-color: #FFF9C4; padding: 8px; "
            "border: 1px solid #FBC02D; border-radius: 5px; "
            "font-size: 10pt;"
        )
        layout.addWidget(info_label)
        
        # 生徒リスト
        self.student_list_widget = QListWidget()
        self.student_list_widget.setDragDropMode(
            QListWidget.DragDropMode.InternalMove
        )
        self.student_list_widget.model().rowsMoved.connect(
            self.on_student_order_changed
        )
        layout.addWidget(self.student_list_widget)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("🔄 リセット")
        reset_btn.clicked.connect(self.reset_assignments)
        button_layout.addWidget(reset_btn)
        
        cancel_btn = QPushButton("✕ キャンセル")
        cancel_btn.clicked.connect(self.on_cancel)
        button_layout.addWidget(cancel_btn)
        
        execute_btn = QPushButton("✓ 分割実行")
        execute_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold;"
        )
        execute_btn.clicked.connect(self.execute_split)
        button_layout.addWidget(execute_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def init_assignments(self):
        """ページ割り当て初期化"""
        current_page = 1
        
        for order, student in enumerate(self.students):
            assignment = StudentPageAssignment(
                student=student,
                start_page=current_page,
                end_page=current_page + self.settings.pages_per_student - 1,
                page_count=self.settings.pages_per_student,
                is_absent=False,
                order=order
            )
            
            self.assignments.append(assignment)
            current_page = assignment.end_page + 1
        
        self.update_student_list()
        self.update_summary()
    
    def update_student_list(self):
        """生徒リスト更新"""
        self.student_list_widget.clear()
        
        for assignment in self.assignments:
            item_widget = StudentAssignmentItem(assignment)
            item_widget.absent_changed.connect(
                lambda: self.recalculate_pages()
            )
            item_widget.pages_changed.connect(
                lambda: self.recalculate_pages()
            )
            item_widget.clicked.connect(
                lambda a=assignment: self.show_student_pages(a)
            )
            
            list_item = QListWidgetItem(self.student_list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.student_list_widget.addItem(list_item)
            self.student_list_widget.setItemWidget(list_item, item_widget)
    
    def recalculate_pages(self):
        """ページ割り当てを再計算"""
        current_page = 1
        
        for assignment in self.assignments:
            if not assignment.is_absent:
                assignment.start_page = current_page
                assignment.end_page = current_page + assignment.page_count - 1
                current_page = assignment.end_page + 1
        
        # UIを更新
        for i in range(self.student_list_widget.count()):
            item = self.student_list_widget.item(i)
            widget = self.student_list_widget.itemWidget(item)
            if isinstance(widget, StudentAssignmentItem):
                widget.update_assignment()
        
        self.update_summary()
    
    def update_summary(self):
        """サマリー更新"""
        total = len(self.assignments)
        absent = sum(1 for a in self.assignments if a.is_absent)
        used_pages = sum(a.page_count for a in self.assignments if not a.is_absent)
        
        self.summary_label.setText(
            f"合計: {total}名 | 欠席: {absent}名 | "
            f"ページ: {used_pages}/{self.total_pages}"
        )
    
    def on_student_order_changed(self):
        """生徒の順番変更時"""
        # リストの順番でassignmentsを並び替え
        new_assignments = []
        for i in range(self.student_list_widget.count()):
            item = self.student_list_widget.item(i)
            widget = self.student_list_widget.itemWidget(item)
            if isinstance(widget, StudentAssignmentItem):
                widget.assignment.order = i
                new_assignments.append(widget.assignment)
        
        self.assignments = new_assignments
        self.recalculate_pages()
    
    def show_student_pages(self, assignment: StudentPageAssignment):
        """生徒のページをプレビュー表示"""
        if not assignment.is_absent and assignment.start_page > 0:
            self.preview_widget.go_to_page(assignment.start_page)
    
    def reset_assignments(self):
        """割り当てをリセット"""
        reply = QMessageBox.question(
            self, "リセット確認",
            "ページ割り当てを初期状態に戻しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.init_assignments()
    
    def load_pdf(self):
        """PDFを読み込み"""
        success = self.preview_widget.load_image(self.pdf_path)
        if success:
            self.total_pages = self.preview_widget.get_total_pages()
            self.update_summary()
            self.update_page_label()
    
    def update_page_label(self):
        """ページラベル更新"""
        current = self.preview_widget.get_current_page()
        total = self.preview_widget.get_total_pages()
        self.page_label.setText(f"{current} / {total}")
    
    def on_cancel(self):
        """キャンセル時"""
        reply = QMessageBox.question(
            self, "確認",
            "PDF分割作業をキャンセルしますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.cancelled.emit()
    
    def execute_split(self):
        """PDF分割を実行"""
        # バリデーション
        is_valid, error_msg = PDFSplitter.validate_assignments(
            self.assignments, self.total_pages
        )
        
        if not is_valid:
            QMessageBox.warning(self, "エラー", error_msg)
            return
        
        # 確認ダイアログ
        active_count = sum(1 for a in self.assignments if not a.is_absent)
        reply = QMessageBox.question(
            self, "分割実行確認",
            f"{active_count}名分のPDFファイルを生成します。\n\n実行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 出力先ディレクトリ選択
        output_dir = QFileDialog.getExistingDirectory(
            self, "出力先ディレクトリを選択"
        )
        
        if not output_dir:
            return
        
        # 分割実行
        try:
            result = PDFSplitter.split_pdf(
                self.pdf_path,
                self.assignments,
                self.grades,
                self.course,
                self.settings,
                output_dir
            )
            
            self.split_completed.emit(result)
            
            # 結果表示
            message = (
                f"PDF分割が完了しました:\n\n"
                f"成功: {result.success_count}件\n"
                f"スキップ: {result.skipped_count}件\n"
                f"エラー: {result.error_count}件\n\n"
                f"出力先: {result.output_dir}"
            )
            
            if result.errors:
                message += f"\n\nエラー詳細:\n"
                message += "\n".join(result.errors[:5])
                if len(result.errors) > 5:
                    message += f"\n... 他 {len(result.errors) - 5}件"
            
            QMessageBox.information(self, "分割完了", message)
            
            # 成功時は自動的に閉じる
            if result.error_count == 0:
                self.cancelled.emit()
        
        except Exception as e:
            logger.error(f"PDF分割エラー: {e}")
            QMessageBox.critical(
                self, "エラー",
                f"PDF分割に失敗しました:\n{str(e)}"
            )
