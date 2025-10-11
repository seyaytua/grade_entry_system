"""PDF分割関連モデル"""

from dataclasses import dataclass
from typing import Optional, List
from models.student import Student


@dataclass
class SplitSettings:
    """PDF分割設定"""
    pages_per_student: int  # 1人あたりのデフォルトページ数
    grade_field: str        # 選択1: 成績項目名（grade1, grade2, ..., note1, note2）
    student_field: str      # 選択2: 生徒情報項目名（note1, note2, note3）
    session_number: str     # 第◯回（例: "4-5"）
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'pages_per_student': self.pages_per_student,
            'grade_field': self.grade_field,
            'student_field': self.student_field,
            'session_number': self.session_number
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SplitSettings':
        """辞書形式から生成"""
        return cls(
            pages_per_student=data['pages_per_student'],
            grade_field=data['grade_field'],
            student_field=data['student_field'],
            session_number=data['session_number']
        )


@dataclass
class StudentPageAssignment:
    """生徒のページ割り当て情報"""
    student: Student        # 生徒オブジェクト
    start_page: int         # 開始ページ（1始まり）
    end_page: int           # 終了ページ（1始まり）
    page_count: int         # ページ数
    is_absent: bool         # 欠席フラグ
    order: int              # 表示順序（ドラッグ&ドロップ対応）
    
    @property
    def page_range(self) -> str:
        """ページ範囲の文字列表現"""
        if self.is_absent:
            return "-"
        return f"{self.start_page}-{self.end_page}"
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'student_number': self.student.student_number,
            'start_page': self.start_page,
            'end_page': self.end_page,
            'page_count': self.page_count,
            'is_absent': self.is_absent,
            'order': self.order
        }


@dataclass
class SplitResult:
    """PDF分割実行結果"""
    success_count: int      # 成功件数
    error_count: int        # エラー件数
    skipped_count: int      # スキップ件数（欠席）
    output_dir: str         # 出力先ディレクトリ
    errors: List[str]       # エラーメッセージリスト
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'success_count': self.success_count,
            'error_count': self.error_count,
            'skipped_count': self.skipped_count,
            'output_dir': self.output_dir,
            'errors': self.errors
        }
