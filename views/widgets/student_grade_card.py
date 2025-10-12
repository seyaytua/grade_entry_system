from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QButtonGroup, QLineEdit, QPushButton,
    QFrame, QMessageBox
)
from PySide6.QtCore import Signal, Qt
import logging

from models.student import Student
from models.grade import Grade
from utils.radio_button_helper import RadioButtonHelper
from config.settings import GRADE_RADIO_OPTIONS

logger = logging.getLogger(__name__)


class StudentGradeCard(QWidget):
    """生徒成績入力カードウィジェット"""
    
    grade_saved = Signal(str)
    
    def __init__(self, student: Student, existing_grade: Grade = None, parent=None):
        super().__init__(parent)
        
        self.student = student
        self.existing_grade = existing_grade
        self.radio_helper = RadioButtonHelper()
        
        self.grade1_group = None
        self.grade2_group = None
        self.grade3_group = None
        
        self.grade4_input = None
        self.grade5_input = None
        self.grade6_input = None
        self.note1_input = None
        self.note2_input = None
        
        self.init_ui()
        
        if existing_grade:
            self.load_grade_data(existing_grade)
    
    def init_ui(self):
        """UI初期化"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        frame.setLineWidth(2)
        frame_layout = QVBoxLayout(frame)
        
        header_layout = QHBoxLayout()
        student_info = QLabel(
            f"<b>No.{self.student.student_number}</b> "
            f"{self.student.student_name} "
            f"({self.student.class_number or ''})"
        )
        student_info.setStyleSheet("font-size: 14pt;")
        header_layout.addWidget(student_info)
        header_layout.addStretch()
        frame_layout.addLayout(header_layout)
        
        grades_layout = QVBoxLayout()
        
        self.grade1_group = self.create_radio_group("成績1:", "grade1")
        grades_layout.addLayout(self.grade1_group[0])
        
        self.grade2_group = self.create_radio_group("成績2:", "grade2")
        grades_layout.addLayout(self.grade2_group[0])
        
        self.grade3_group = self.create_radio_group("成績3:", "grade3")
        grades_layout.addLayout(self.grade3_group[0])
        
        numeric_layout = QHBoxLayout()
        
        self.grade4_input = QLineEdit()
        self.grade4_input.setPlaceholderText("成績4")
        self.grade4_input.setMaximumWidth(100)
        numeric_layout.addWidget(QLabel("成績4:"))
        numeric_layout.addWidget(self.grade4_input)
        
        self.grade5_input = QLineEdit()
        self.grade5_input.setPlaceholderText("成績5")
        self.grade5_input.setMaximumWidth(100)
        numeric_layout.addWidget(QLabel("成績5:"))
        numeric_layout.addWidget(self.grade5_input)
        
        self.grade6_input = QLineEdit()
        self.grade6_input.setPlaceholderText("成績6")
        self.grade6_input.setMaximumWidth(100)
        numeric_layout.addWidget(QLabel("成績6:"))
        numeric_layout.addWidget(self.grade6_input)
        
        numeric_layout.addStretch()
        grades_layout.addLayout(numeric_layout)
        
        note_layout = QHBoxLayout()
        
        self.note1_input = QLineEdit()
        self.note1_input.setPlaceholderText("備考1")
        note_layout.addWidget(QLabel("備考1:"))
        note_layout.addWidget(self.note1_input)
        
        self.note2_input = QLineEdit()
        self.note2_input.setPlaceholderText("備考2")
        note_layout.addWidget(QLabel("備考2:"))
        note_layout.addWidget(self.note2_input)
        
        grades_layout.addLayout(note_layout)
        frame_layout.addLayout(grades_layout)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        clear_btn = QPushButton("クリア")
        clear_btn.clicked.connect(self.clear_inputs)
        button_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        save_btn.clicked.connect(self.save_grade)
        button_layout.addWidget(save_btn)
        
        frame_layout.addLayout(button_layout)
        layout.addWidget(frame)
    
    def create_radio_group(self, label: str, group_name: str):
        """ラジオボタングループを作成"""
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        
        button_group = QButtonGroup(self)
        button_group.setExclusive(False)
        
        buttons = []
        for value, text in GRADE_RADIO_OPTIONS:
            radio = QRadioButton(text)
            radio.setProperty("value", value)
            radio.clicked.connect(
                lambda checked, btn=radio, gname=group_name, bg=button_group:
                self.on_radio_clicked(btn, gname, bg)
            )
            button_group.addButton(radio)
            layout.addWidget(radio)
            buttons.append(radio)
        
        layout.addStretch()
        return (layout, button_group, buttons)
    
    def on_radio_clicked(self, button: QRadioButton, group_name: str, button_group: QButtonGroup):
        """ラジオボタンクリック時の処理"""
        is_deselected = self.radio_helper.handle_click(button, group_name, button_group)
        
        if not is_deselected:
            for btn in button_group.buttons():
                if btn != button:
                    btn.setChecked(False)
    
    def get_selected_radio_value(self, button_group: QButtonGroup):
        """選択されているラジオボタンの値を取得"""
        for button in button_group.buttons():
            if button.isChecked():
                return button.property("value")
        return None
    
    def load_grade_data(self, grade: Grade):
        """既存の成績データを読み込む"""
        if grade.grade1 is not None:
            for btn in self.grade1_group[1].buttons():
                if btn.property("value") == grade.grade1:
                    btn.setChecked(True)
        
        if grade.grade2 is not None:
            for btn in self.grade2_group[1].buttons():
                if btn.property("value") == grade.grade2:
                    btn.setChecked(True)
        
        if grade.grade3 is not None:
            for btn in self.grade3_group[1].buttons():
                if btn.property("value") == grade.grade3:
                    btn.setChecked(True)
        
        if grade.grade4 is not None:
            self.grade4_input.setText(str(grade.grade4))
        if grade.grade5 is not None:
            self.grade5_input.setText(str(grade.grade5))
        if grade.grade6 is not None:
            self.grade6_input.setText(str(grade.grade6))
        
        if grade.note1:
            self.note1_input.setText(grade.note1)
        if grade.note2:
            self.note2_input.setText(grade.note2)
    
    def get_grade_data(self):
        """入力された成績データを取得"""
        data = {
            'student_number': self.student.student_number,
            'grade1': self.get_selected_radio_value(self.grade1_group[1]),
            'grade2': self.get_selected_radio_value(self.grade2_group[1]),
            'grade3': self.get_selected_radio_value(self.grade3_group[1]),
            'grade4': None,
            'grade5': None,
            'grade6': None,
            'note1': self.note1_input.text().strip() or None,
            'note2': self.note2_input.text().strip() or None
        }
        
        try:
            if self.grade4_input.text().strip():
                data['grade4'] = float(self.grade4_input.text())
        except ValueError:
            pass
        
        try:
            if self.grade5_input.text().strip():
                data['grade5'] = float(self.grade5_input.text())
        except ValueError:
            pass
        
        try:
            if self.grade6_input.text().strip():
                data['grade6'] = float(self.grade6_input.text())
        except ValueError:
            pass
        
        return data
    
    def clear_inputs(self):
        """入力をクリア"""
        for btn in self.grade1_group[1].buttons():
            btn.setAutoExclusive(False)
            btn.setChecked(False)
            btn.setAutoExclusive(True)
        
        for btn in self.grade2_group[1].buttons():
            btn.setAutoExclusive(False)
            btn.setChecked(False)
            btn.setAutoExclusive(True)
        
        for btn in self.grade3_group[1].buttons():
            btn.setAutoExclusive(False)
            btn.setChecked(False)
            btn.setAutoExclusive(True)
        
        self.grade4_input.clear()
        self.grade5_input.clear()
        self.grade6_input.clear()
        self.note1_input.clear()
        self.note2_input.clear()
        
        self.radio_helper.reset_all()
        logger.debug(f"入力をクリアしました: {self.student.student_name}")
    
    def save_grade(self):
        """成績を保存"""
        try:
            grade_data = self.get_grade_data()
            self.grade_saved.emit(self.student.student_number)
            logger.info(f"成績を保存しました: {self.student.student_name}")
        except Exception as e:
            logger.error(f"成績保存エラー: {e}")
            QMessageBox.critical(self, "エラー", f"成績の保存に失敗しました:\n{str(e)}")
