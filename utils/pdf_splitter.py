"""PDF分割ユーティリティ"""

import logging
from pathlib import Path
from typing import Dict
from PyPDF2 import PdfReader, PdfWriter

from models.student import Student
from models.grade import Grade
from models.course import Course
from models.split import StudentPageAssignment, SplitResult

logger = logging.getLogger(__name__)


class PDFSplitter:
    """PDF分割処理を行うユーティリティクラス"""
    
    @staticmethod
    def split_pdf(
        pdf_path: str,
        assignments: list[StudentPageAssignment],
        grades: Dict[str, Grade],
        course: Course,
        settings,
        output_dir: str
    ) -> SplitResult:
        """
        PDFを分割して保存
        
        Args:
            pdf_path: PDFファイルのパス
            assignments: 生徒のページ割り当てリスト
            grades: 成績データ（生徒番号 -> Grade）
            course: 講座オブジェクト
            settings: 分割設定
            output_dir: 出力先ディレクトリ
            
        Returns:
            分割結果
        """
        result = SplitResult(
            success_count=0,
            error_count=0,
            skipped_count=0,
            output_dir=output_dir,
            errors=[]
        )
        
        try:
            # PDFを読み込み
            reader = PdfReader(pdf_path)
            
            for assignment in assignments:
                try:
                    # 欠席者はスキップ
                    if assignment.is_absent:
                        result.skipped_count += 1
                        continue
                    
                    student = assignment.student
                    grade = grades.get(student.student_number)
                    
                    # ファイル名生成
                    filename = PDFSplitter._generate_filename(
                        student, grade, course, settings
                    )
                    output_path = Path(output_dir) / filename
                    
                    # 新しいPDFライター作成
                    writer = PdfWriter()
                    
                    # 指定ページ範囲を追加
                    for page_num in range(
                        assignment.start_page - 1,  # 0始まりに変換
                        assignment.end_page
                    ):
                        if page_num < len(reader.pages):
                            writer.add_page(reader.pages[page_num])
                        else:
                            raise ValueError(
                                f"ページ {page_num + 1} は存在しません"
                            )
                    
                    # ファイルに書き込み
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    result.success_count += 1
                    logger.info(f"PDF分割成功: {filename}")
                
                except Exception as e:
                    result.error_count += 1
                    error_msg = f"{student.student_name}: {str(e)}"
                    result.errors.append(error_msg)
                    logger.error(f"PDF分割エラー: {error_msg}")
            
            return result
        
        except Exception as e:
            logger.error(f"PDF読み込みエラー: {e}")
            raise
    
    @staticmethod
    def _generate_filename(student: Student, grade, course: Course, settings) -> str:
        """
        ファイル名を生成
        
        フォーマット: {クラス番号}_{氏名}_{講座名}_第{回数}回_{選択1の値}_{選択2の値}.pdf
        """
        # クラス番号
        class_number = student.class_number or "未設定"
        
        # 氏名（スペース削除）
        student_name = student.student_name.replace(" ", "").replace("　", "")
        
        # 講座名
        course_name = course.course_name
        
        # 第◯回
        session = f"第{settings.session_number}回" if settings.session_number else ""
        
        # 選択1（成績項目）
        grade_value = ""
        if grade:
            grade_value = str(getattr(grade, settings.grade_field, ""))
        
        # 選択2（生徒情報項目）
        student_value = str(getattr(student, settings.student_field, ""))
        
        # ファイル名組み立て
        parts = [
            class_number,
            student_name,
            course_name,
            session,
            grade_value,
            student_value
        ]
        
        # 空の要素を除外
        parts = [p for p in parts if p]
        
        filename = "_".join(parts) + ".pdf"
        
        # ファイル名の不正文字を置換
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename
    
    @staticmethod
    def validate_assignments(
        assignments: list[StudentPageAssignment],
        total_pages: int
    ) -> tuple[bool, str]:
        """
        ページ割り当てを検証
        
        Args:
            assignments: 生徒のページ割り当てリスト
            total_pages: PDFの総ページ数
            
        Returns:
            (検証結果, エラーメッセージ)
        """
        # 割り当てページ数の合計
        used_pages = sum(
            a.page_count for a in assignments if not a.is_absent
        )
        
        if used_pages > total_pages:
            return False, f"割り当てページ数（{used_pages}）が総ページ数（{total_pages}）を超えています"
        
        # 重複チェック
        page_map = {}
        for assignment in assignments:
            if assignment.is_absent:
                continue
            
            for page in range(assignment.start_page, assignment.end_page + 1):
                if page in page_map:
                    return False, f"ページ {page} が重複しています"
                page_map[page] = assignment.student.student_name
        
        return True, ""
