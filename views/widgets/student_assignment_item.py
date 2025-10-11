"""生徒のページ割り当てアイテムウィジェット"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging

from models.split import StudentPageAssignment

logger = logging.getLogger(__name__)


class StudentAssignmentItem(QWidget):
    """生徒のページ割り当てアイテム"""
    
    # シグナル
    absent_changed = pyqtSignal(bool)  # 欠席状態変更
    pages_changed = pyqtSignal(int, int)  # ページ範囲変更
    clicked = pyqtSignal()  # クリックされた
    
    def __init__(self, assignment: StudentPageAssignment, parent=None):
        super().__init__(parent)
        
        self.assignment = assignment
        
        self.start_page_input: QSpinBox
        self.end_page_input: QSpinBox
        self.page_count_input: QSpinBox
        self.absent_checkbox: QCheckBox
        
        self.init_ui()
    
    def init_ui(self):
        """UI初期化"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 生徒情報行
        info_layout = QHBoxLayout()
        
        # 生徒番号・氏名
        name_label = QLabel(
            f"{self.assignment.student.class_number or '未設定'} "
            f"{self.assignment.student.student_name}"
        )
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(name_label)
        
        info_layout.addStretch()
        
        # 欠席チェックボックス（重要：排他的動作を無効化）
        self.absent_checkbox = QCheckBox("欠席")
        self.absent_checkbox.setAutoExclusive(False)  # これが重要！
        self.absent_checkbox.setTristate(False)  # 3状態を無効化
        self.absent_checkbox.setChecked(self.assignment.is_absent)
        self.absent_checkbox.stateChanged.connect(self.on_absent_changed)
        info_layout.addWidget(self.absent_checkbox)
        
        layout.addLayout(info_layout)
        
        # ページ割り当て行
        page_layout = QHBoxLayout()
        
        page_layout.addWidget(QLabel("ページ:"))
        
        self.start_page_input = QSpinBox()
        self.start_page_input.setMinimum(1)
        self.start_page_input.setMaximum(9999)
        self.start_page_input.setValue(self.assignment.start_page)
        self.start_page_input.valueChanged.connect(self.on_page_changed)
        page_layout.addWidget(self.start_page_input)
        
        page_layout.addWidget(QLabel("〜"))
        
        self.end_page_input = QSpinBox()
        self.end_page_input.setMinimum(1)
        self.end_page_input.setMaximum(9999)
        self.end_page_input.setValue(self.assignment.end_page)
        self.end_page_input.valueChanged.connect(self.on_page_changed)
        page_layout.addWidget(self.end_page_input)
        
        page_layout.addWidget(QLabel("枚数:"))
        
        self.page_count_input = QSpinBox()
        self.page_count_input.setMinimum(1)
        self.page_count_input.setMaximum(10)
        self.page_count_input.setValue(self.assignment.page_count)
        self.page_count_input.valueChanged.connect(self.on_page_count_changed)
        page_layout.addWidget(self.page_count_input)
        
        page_layout.addStretch()
        
        layout.addLayout(page_layout)
        
        # 初期スタイル設定
        self.update_style()
    
    def update_style(self):
        """スタイルを更新"""
        if self.assignment.is_absent:
            self.setStyleSheet("""
                StudentAssignmentItem {
                    background: #FFEBEE;
                    border: 2px solid #EF5350;
                    border-radius: 6px;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                StudentAssignmentItem {
                    background: #f9f9f9;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 5px;
                }
                StudentAssignmentItem:hover {
                    border-color: #2196F3;
                }
            """)
    
    def on_absent_changed(self, state):
        """欠席状態変更時"""
        is_absent = (state == Qt.CheckState.Checked.value)
        self.assignment.is_absent = is_absent
        
        # 入力フィールドを無効化/有効化
        self.start_page_input.setEnabled(not is_absent)
        self.end_page_input.setEnabled(not is_absent)
        self.page_count_input.setEnabled(not is_absent)
        
        # スタイル更新
        self.update_style()
        
        # シグナル発行
        self.absent_changed.emit(is_absent)
        
        logger.debug(f"欠席状態変更: {self.assignment.student.student_name} -> {is_absent}")
    
    def on_page_changed(self):
        """ページ範囲変更時"""
        start = self.start_page_input.value()
        end = self.end_page_input.value()
        
        if end < start:
            end = start
            self.end_page_input.setValue(end)
        
        self.assignment.start_page = start
        self.assignment.end_page = end
        self.assignment.page_count = end - start + 1
        
        # 枚数を更新
        self.page_count_input.blockSignals(True)
        self.page_count_input.setValue(self.assignment.page_count)
        self.page_count_input.blockSignals(False)
        
        self.pages_changed.emit(start, end)
    
    def on_page_count_changed(self, count):
        """ページ数変更時"""
        self.assignment.page_count = count
        self.assignment.end_page = self.assignment.start_page + count - 1
        
        # 終了ページを更新
        self.end_page_input.blockSignals(True)
        self.end_page_input.setValue(self.assignment.end_page)
        self.end_page_input.blockSignals(False)
        
        self.pages_changed.emit(self.assignment.start_page, self.assignment.end_page)
    
    def mousePressEvent(self, event):
        """マウスクリック時"""
        self.clicked.emit()
        super().mousePressEvent(event)
    
    def update_assignment(self):
        """表示を更新"""
        self.start_page_input.blockSignals(True)
        self.end_page_input.blockSignals(True)
        self.page_count_input.blockSignals(True)
        self.absent_checkbox.blockSignals(True)
        
        self.start_page_input.setValue(self.assignment.start_page)
        self.end_page_input.setValue(self.assignment.end_page)
        self.page_count_input.setValue(self.assignment.page_count)
        self.absent_checkbox.setChecked(self.assignment.is_absent)
        
        self.start_page_input.blockSignals(False)
        self.end_page_input.blockSignals(False)
        self.page_count_input.blockSignals(False)
        self.absent_checkbox.blockSignals(False)
        
        self.update_style()
