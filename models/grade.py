from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Grade:
    """成績モデル"""
    id: Optional[int]
    course_id: int
    entry_date: str
    student_number: str
    grade1: Optional[int] = None
    grade2: Optional[int] = None
    grade3: Optional[int] = None
    grade4: Optional[float] = None
    grade5: Optional[float] = None
    grade6: Optional[float] = None
    note1: Optional[str] = None
    note2: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'entry_date': self.entry_date,
            'student_number': self.student_number,
            'grade1': self.grade1,
            'grade2': self.grade2,
            'grade3': self.grade3,
            'grade4': self.grade4,
            'grade5': self.grade5,
            'grade6': self.grade6,
            'note1': self.note1,
            'note2': self.note2,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Grade':
        """辞書形式から生成"""
        return cls(
            id=data.get('id'),
            course_id=data['course_id'],
            entry_date=data['entry_date'],
            student_number=data['student_number'],
            grade1=data.get('grade1'),
            grade2=data.get('grade2'),
            grade3=data.get('grade3'),
            grade4=data.get('grade4'),
            grade5=data.get('grade5'),
            grade6=data.get('grade6'),
            note1=data.get('note1'),
            note2=data.get('note2'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


@dataclass
class GradeListItem:
    """成績一覧表示用モデル"""
    id: int
    course_id: int
    course_name: str
    entry_date: str
    student_number: str
    student_name: str
    class_number: Optional[str]
    grade1: Optional[int]
    grade2: Optional[int]
    grade3: Optional[int]
    grade4: Optional[float]
    grade5: Optional[float]
    grade6: Optional[float]
    note1: Optional[str]
    note2: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GradeListItem':
        """辞書形式から生成"""
        return cls(
            id=data['id'],
            course_id=data['course_id'],
            course_name=data['course_name'],
            entry_date=data['entry_date'],
            student_number=data['student_number'],
            student_name=data['student_name'],
            class_number=data.get('class_number'),
            grade1=data.get('grade1'),
            grade2=data.get('grade2'),
            grade3=data.get('grade3'),
            grade4=data.get('grade4'),
            grade5=data.get('grade5'),
            grade6=data.get('grade6'),
            note1=data.get('note1'),
            note2=data.get('note2'),
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )
