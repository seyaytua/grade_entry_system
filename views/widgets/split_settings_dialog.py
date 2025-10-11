"""PDF分割設定ダイアログ"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QLineEdit, QComboBox, QDialogButtonBox,
    QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
import logging

from models.split import SplitSettings

logger = logging.getLogger(__name__)


class SplitSettingsDialog(QDialog):
    """PDF分割設定ダイアログ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.pages_per_student_input: QSpinBox
        self.session_number_input: QLineEdit
        self.grade_field_combo: QComboBox
        self.student_field_combo: QComboBox
        
        self.init_ui()
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("PDF分割設定")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 説明
        info_label = QLabel(
            "PDFファイルを生徒ごとに分割します。\n"
            "各生徒のページ数とファイル名の構成要素を設定してください。"
        )
        info_label.setStyleSheet("background-color: #E3F2FD; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # 基本設定グループ
        basic_group = QGroupBox("基本設定")
        basic_layout = QVBoxLayout(basic_group)
        
        # 1人あたりのページ数
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("1人あたりのページ数:"))
        
        self.pages_per_student_input = QSpinBox()
        self.pages_per_student_input.setMinimum(1)
        self.pages_per_student_input.setMaximum(10)
        self.pages_per_student_input.setValue(2)
        self.pages_per_student_input.setToolTip("全生徒に一律適用される初期値")
        pages_layout.addWidget(self.pages_per_student_input)
        
        pages_layout.addWidget(QLabel("ページ"))
        pages_layout.addStretch()
        
        basic_layout.addLayout(pages_layout)
        
        # 第◯回
        session_layout = QHBoxLayout()
        session_layout.addWidget(QLabel("第◯回:"))
        
        self.session_number_input = QLineEdit()
        self.session_number_input.setPlaceholderText("例: 4-5")
        self.session_number_input.setToolTip("ファイル名の「第◯回」部分（空白可）")
        session_layout.addWidget(self.session_number_input)
        
        session_layout.addStretch()
        
        basic_layout.addLayout(session_layout)
        
        layout.addWidget(basic_group)
        
        # ファイル名設定グループ
        filename_group = QGroupBox("ファイル名設定")
        filename_layout = QVBoxLayout(filename_group)
        
        filename_info = QLabel(
            "フォーマット: {クラス番号}_{氏名}_{講座名}_第{回数}回_{選択1の値}_{選択2の値}.pdf"
        )
        filename_info.setStyleSheet("color: #666; font-size: 10pt;")
        filename_layout.addWidget(filename_info)
        
        # 選択1（成績項目）
        grade_layout = QHBoxLayout()
        grade_layout.addWidget(QLabel("選択1（成績項目）:"))
        
        self.grade_field_combo = QComboBox()
        self.grade_field_combo.addItem("成績1 (grade1)", "grade1")
        self.grade_field_combo.addItem("成績2 (grade2)", "grade2")
        self.grade_field_combo.addItem("成績3 (grade3)", "grade3")
        self.grade_field_combo.addItem("成績4 (grade4)", "grade4")
        self.grade_field_combo.addItem("成績5 (grade5)", "grade5")
        self.grade_field_combo.addItem("成績6 (grade6)", "grade6")
        self.grade_field_combo.addItem("備考1 (note1)", "note1")
        self.grade_field_combo.addItem("備考2 (note2)", "note2")
        self.grade_field_combo.setToolTip("ファイル名に含める成績項目")
        grade_layout.addWidget(self.grade_field_combo, 1)
        
        filename_layout.addLayout(grade_layout)
        
        # 選択2（生徒情報項目）
        student_layout = QHBoxLayout()
        student_layout.addWidget(QLabel("選択2（生徒情報）:"))
        
        self.student_field_combo = QComboBox()
        self.student_field_combo.addItem("備考1 (note1)", "note1")
        self.student_field_combo.addItem("備考2 (note2)", "note2")
        self.student_field_combo.addItem("備考3 (note3)", "note3")
        self.student_field_combo.setToolTip("ファイル名に含める生徒情報項目")
        student_layout.addWidget(self.student_field_combo, 1)
        
        filename_layout.addLayout(student_layout)
        
        layout.addWidget(filename_group)
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("次へ（分割作業画面）")
        
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("キャンセル")
        
        layout.addWidget(button_box)
    
    def get_settings(self) -> SplitSettings:
        """設定を取得"""
        return SplitSettings(
            pages_per_student=self.pages_per_student_input.value(),
            grade_field=self.grade_field_combo.currentData(),
            student_field=self.student_field_combo.currentData(),
            session_number=self.session_number_input.text().strip()
        )
    
    def accept(self):
        """OK押下時の検証"""
        if self.pages_per_student_input.value() < 1:
            QMessageBox.warning(
                self, "入力エラー",
                "1人あたりのページ数は1以上を指定してください"
            )
            return
        
        super().accept()
