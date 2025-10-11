from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QDateEdit, QPushButton, QScrollArea,
    QFileDialog, QMessageBox, QDialog, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QDate
import logging
from pathlib import Path

from database.repositories.course_repository import CourseRepository
from database.repositories.student_repository import StudentRepository
from database.repositories.grade_repository import GradeRepository
from models.grade import Grade
from views.widgets.image_preview_widget import ImagePreviewWidget
from views.widgets.student_grade_card import StudentGradeCard
from config.settings import SUPPORTED_IMAGE_FORMATS
from views.widgets.split_settings_dialog import SplitSettingsDialog
from views.pdf_split_view import PDFSplitView
from models.split import SplitSettings


logger = logging.getLogger(__name__)


class GradeEntryView(QWidget):
    """成績入力ビュー"""
    
    def __init__(self, course_repo: CourseRepository,
                 student_repo: StudentRepository,
                 grade_repo: GradeRepository,
                 parent=None):
        super().__init__(parent)
        
        self.course_repo = course_repo
        self.student_repo = student_repo
        self.grade_repo = grade_repo
        
        self.current_course_id = None
        self.current_entry_date = None
        self.student_cards = []
        
        self.init_ui()
        self.refresh_courses()
    
    def init_ui(self):
        """UI初期化"""
        layout = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左側: プレビューエリア
        left_widget = self.create_preview_area()
        splitter.addWidget(left_widget)
        
        # 右側: 成績入力エリア
        right_widget = self.create_entry_area()
        splitter.addWidget(right_widget)
        
        # 分割比率を 6:4 に設定
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        
        layout.addWidget(splitter)
    
    def create_preview_area(self):
        """画像プレビューエリアを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ファイル選択ボタン
        file_layout = QHBoxLayout()
        select_btn = QPushButton("ファイル選択")
        select_btn.clicked.connect(self.select_image_file)
        file_layout.addWidget(select_btn)
        file_layout.addStretch()
        layout.addLayout(file_layout)
        
        # ズームコントロール
        control_layout = QHBoxLayout()
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.clicked.connect(self.zoom_out)
        control_layout.addWidget(zoom_out_btn)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setMinimumWidth(60)
        control_layout.addWidget(self.zoom_label)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.clicked.connect(self.zoom_in)
        control_layout.addWidget(zoom_in_btn)
        
        reset_btn = QPushButton("⟲")
        reset_btn.clicked.connect(self.reset_zoom)
        control_layout.addWidget(reset_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # ページ送りコントロール（PDF用）
        page_layout = QHBoxLayout()
        
        self.prev_page_btn = QPushButton("◀ 前のページ")
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.prev_page_btn.setEnabled(False)
        page_layout.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel("1 / 1")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setMinimumWidth(80)
        page_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton("次のページ ▶")
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setEnabled(False)
        page_layout.addWidget(self.next_page_btn)
        
        page_layout.addStretch()
        layout.addLayout(page_layout)
        
        # 画像プレビュー
        self.image_preview = ImagePreviewWidget()
        layout.addWidget(self.image_preview)
        
        return widget
    
    def create_entry_area(self):
        """成績入力エリアを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 講座・日付選択
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("講座:"))
        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(self.on_course_changed)
        select_layout.addWidget(self.course_combo, 1)
        
        select_layout.addWidget(QLabel("授業日:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self.on_date_changed)
        select_layout.addWidget(self.date_edit)
        
        load_btn = QPushButton("読み込み")
        load_btn.clicked.connect(self.load_students)
        select_layout.addWidget(load_btn)
        layout.addLayout(select_layout)
        
        # サマリーバー
        self.summary_label = QLabel("講座と日付を選択してください")
        self.summary_label.setStyleSheet(
            "background-color: #E3F2FD; padding: 10px; "
            "border: 1px solid #2196F3; border-radius: 5px;"
        )
        layout.addWidget(self.summary_label)
        
        # 生徒カードスクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.addStretch()
        
        scroll.setWidget(self.cards_widget)
        layout.addWidget(scroll)
        

        # PDF分割ボタン
        split_btn = QPushButton("📄 PDF分割")
        split_btn.setStyleSheet(
            "background-color: #FF9800; color: white; "
            "font-weight: bold; font-size: 14pt; padding: 10px;"
        )
        split_btn.clicked.connect(self.open_split_dialog)
        layout.addWidget(split_btn)
        
        # 一括保存ボタン
        save_all_btn = QPushButton("全ての成績を一括保存")
        save_all_btn.setStyleSheet(
            "background-color: #2196F3; color: white; "
            "font-weight: bold; font-size: 14pt; padding: 10px;"
        )
        save_all_btn.clicked.connect(self.save_all_grades)
        layout.addWidget(save_all_btn)
        
        return widget
    
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
            QMessageBox.critical(self, "エラー", f"講座リストの更新に失敗しました:\n{str(e)}")
    
    def on_course_changed(self):
        """講座変更時の処理"""
        self.current_course_id = self.course_combo.currentData()
        self.clear_student_cards()
        self.update_summary()
    
    def on_date_changed(self):
        """日付変更時の処理"""
        self.current_entry_date = self.date_edit.date().toString("yyyy-MM-dd")
        self.clear_student_cards()
        self.update_summary()
    
    def load_students(self):
        """生徒リストを読み込む"""
        if not self.current_course_id:
            QMessageBox.warning(self, "警告", "講座を選択してください")
            return
        
        try:
            self.current_entry_date = self.date_edit.date().toString("yyyy-MM-dd")
            students = self.student_repo.get_students_by_course(self.current_course_id)
            
            if not students:
                QMessageBox.information(self, "情報", "この講座に登録されている生徒がいません")
                return
            
            # 既存の成績を取得
            existing_grades = self.grade_repo.get_grades_by_course_date(
                self.current_course_id, self.current_entry_date
            )
            grades_dict = {g.student_number: g for g in existing_grades}
            
            self.clear_student_cards()
            
            # 生徒カードを生成
            for student in students:
                existing_grade = grades_dict.get(student.student_number)
                card = StudentGradeCard(student, existing_grade)
                card.grade_saved.connect(self.on_grade_saved)
                self.student_cards.append(card)
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            
            self.update_summary()
            logger.info(f"生徒を読み込みました ({len(students)}名)")
        except Exception as e:
            logger.error(f"生徒読み込みエラー: {e}")
            QMessageBox.critical(self, "エラー", f"生徒の読み込みに失敗しました:\n{str(e)}")
    
    def clear_student_cards(self):
        """生徒カードをクリア"""
        for card in self.student_cards:
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        self.student_cards.clear()
    
    def update_summary(self):
        """サマリーを更新"""
        if not self.student_cards:
            self.summary_label.setText("講座と日付を選択してください")
            return
        
        entered = sum(1 for card in self.student_cards 
                     if any(v for v in card.get_grade_data().values() if v is not None))
        total = len(self.student_cards)
        self.summary_label.setText(f"登録: {total}名 | 入力済: {entered}名 | 未入力: {total - entered}名")
    
    def on_grade_saved(self, student_number: str):
        """個別保存時の処理"""
        try:
            card = next((c for c in self.student_cards 
                        if c.student.student_number == student_number), None)
            if not card:
                return
            
            grade_data = card.get_grade_data()
            grade = Grade(
                id=None,
                course_id=self.current_course_id,
                entry_date=self.current_entry_date,
                student_number=student_number,
                grade1=grade_data['grade1'],
                grade2=grade_data['grade2'],
                grade3=grade_data['grade3'],
                grade4=grade_data['grade4'],
                grade5=grade_data['grade5'],
                grade6=grade_data['grade6'],
                note1=grade_data['note1'],
                note2=grade_data['note2']
            )
            self.grade_repo.create_or_update_grade(grade)
            self.update_summary()
            QMessageBox.information(self, "保存完了", "成績を保存しました")
        except Exception as e:
            logger.error(f"成績保存エラー: {e}")
            QMessageBox.critical(self, "エラー", f"成績の保存に失敗しました:\n{str(e)}")
    
    def save_all_grades(self):
        """全成績を一括保存"""
        if not self.student_cards:
            QMessageBox.warning(self, "警告", "保存する成績がありません")
            return
        
        try:
            saved_count = 0
            for card in self.student_cards:
                grade_data = card.get_grade_data()
                
                # 何か入力されている場合のみ保存
                if not any([grade_data['grade1'], grade_data['grade2'], grade_data['grade3'],
                           grade_data['grade4'], grade_data['grade5'], grade_data['grade6']]):
                    continue
                
                grade = Grade(
                    id=None,
                    course_id=self.current_course_id,
                    entry_date=self.current_entry_date,
                    student_number=grade_data['student_number'],
                    grade1=grade_data['grade1'],
                    grade2=grade_data['grade2'],
                    grade3=grade_data['grade3'],
                    grade4=grade_data['grade4'],
                    grade5=grade_data['grade5'],
                    grade6=grade_data['grade6'],
                    note1=grade_data['note1'],
                    note2=grade_data['note2']
                )
                self.grade_repo.create_or_update_grade(grade)
                saved_count += 1
            
            self.update_summary()
            QMessageBox.information(self, "保存完了", f"{saved_count}名分の成績を保存しました")
            logger.info(f"一括保存完了: {saved_count}名")
        except Exception as e:
            logger.error(f"一括保存エラー: {e}")
            QMessageBox.critical(self, "エラー", f"一括保存に失敗しました:\n{str(e)}")
    
    def select_image_file(self):
        """画像ファイルを選択"""
        # PDFをデフォルトに変更
        file_filter = "PDFファイル (*.pdf);;画像ファイル (*.png *.jpg *.jpeg);;全てのファイル (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選択", "", file_filter
        )
        
        if file_path:
            success = self.image_preview.load_image(file_path)
            if success:
                self.update_zoom_label()
                self.update_page_controls()
            # エラーメッセージは ImagePreviewWidget 内で表示
    
    def update_page_controls(self):
        """ページ送りコントロールを更新"""
        total_pages = self.image_preview.get_total_pages()
        current_page = self.image_preview.get_current_page()
        
        if total_pages > 1:
            self.prev_page_btn.setEnabled(current_page > 1)
            self.next_page_btn.setEnabled(current_page < total_pages)
            self.page_label.setText(f"{current_page} / {total_pages}")
        else:
            self.prev_page_btn.setEnabled(False)
            self.next_page_btn.setEnabled(False)
            self.page_label.setText("1 / 1")
    
    def prev_page(self):
        """前のページへ"""
        self.image_preview.prev_page()
        self.update_page_controls()
    
    def next_page(self):
        """次のページへ"""
        self.image_preview.next_page()
        self.update_page_controls()
    
    def zoom_in(self):
        """拡大"""
        self.image_preview.zoom_in()
        self.update_zoom_label()
    
    def zoom_out(self):
        """縮小"""
        self.image_preview.zoom_out()
        self.update_zoom_label()
    
    def reset_zoom(self):
        """ズームリセット"""
        self.image_preview.reset_zoom()
        self.update_zoom_label()
    
    def update_zoom_label(self):
        """ズームラベルを更新"""
        percentage = self.image_preview.get_zoom_percentage()
        self.zoom_label.setText(f"{percentage}%")
    
    def open_split_dialog(self):
        """PDF分割ダイアログを開く"""
        try:
            # PDFファイルが読み込まれているか確認
            pdf_path = getattr(self.image_preview, 'current_file_path', None)
            
            if not pdf_path:
                QMessageBox.warning(
                    self, "警告",
                    "画像またはPDFファイルを読み込んでください"
                )
                return
            
            if not pdf_path.lower().endswith('.pdf'):
                QMessageBox.warning(
                    self, "警告",
                    "PDFファイルを読み込んでください"
                )
                return
            
            # 講座と生徒が選択されているか確認
            if not self.current_course_id or not self.student_cards:
                QMessageBox.warning(
                    self, "警告",
                    "講座と生徒を読み込んでください"
                )
                return
            
            # 分割設定ダイアログ表示
            dialog = SplitSettingsDialog(self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                settings = dialog.get_settings()
                
                # 現在の生徒リストと成績を取得
                students = [card.student for card in self.student_cards]
                grades = {}
                
                for card in self.student_cards:
                    grade_data = card.get_grade_data()
                    from models.grade import Grade
                    grade = Grade(
                        id=None,
                        course_id=self.current_course_id,
                        entry_date=self.current_entry_date,
                        student_number=grade_data['student_number'],
                        grade1=grade_data['grade1'],
                        grade2=grade_data['grade2'],
                        grade3=grade_data['grade3'],
                        grade4=grade_data['grade4'],
                        grade5=grade_data['grade5'],
                        grade6=grade_data['grade6'],
                        note1=grade_data['note1'],
                        note2=grade_data['note2']
                    )
                    grades[grade_data['student_number']] = grade
                
                # 現在の講座を取得
                course = self.course_repo.get_course_by_id(self.current_course_id)
                
                # PDF分割作業画面を表示
                self.show_split_view(pdf_path, students, grades, course, settings)
        
        except Exception as e:
            logger.error(f"PDF分割ダイアログエラー: {e}", exc_info=True)
            QMessageBox.critical(
                self, "エラー",
                f"PDF分割ダイアログでエラーが発生しました:\n{str(e)}"
            )
    
    def show_split_view(self, pdf_path, students, grades, course, settings):
        """PDF分割作業画面を表示"""
        try:
            split_view = PDFSplitView(
                pdf_path, students, grades, course, settings, self
            )
            
            # 新しいウィンドウで表示
            split_window = QDialog(self)
            split_window.setWindowTitle("PDF分割作業")
            split_window.setMinimumSize(1400, 900)
            
            layout = QVBoxLayout(split_window)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(split_view)
            
            # シグナル接続
            split_view.split_completed.connect(
                lambda result: self.on_split_completed(result, split_window)
            )
            split_view.cancelled.connect(split_window.close)
            
            split_window.exec()
        
        except Exception as e:
            logger.error(f"PDF分割ビュー表示エラー: {e}", exc_info=True)
            QMessageBox.critical(
                self, "エラー",
                f"PDF分割画面の表示に失敗しました:\n{str(e)}"
            )
    
    def on_split_completed(self, result, split_window=None):
        """PDF分割完了時"""
        logger.info(f"PDF分割完了: 成功={result.success_count}, エラー={result.error_count}")
        if split_window:
            split_window.close()
