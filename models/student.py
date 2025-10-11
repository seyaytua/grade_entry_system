from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Student:
    """生徒モデル"""
    id: Optional[int]
    course_id: int
    student_number: str
    class_number: Optional[str]
    student_name: str
    note1: Optional[str] = None
    note2: Optional[str] = None
    note3: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'student_number': self.student_number,
            'class_number': self.class_number,
            'student_name': self.student_name,
            'note1': self.note1,
            'note2': self.note2,
            'note3': self.note3,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        """辞書形式から生成"""
        return cls(
            id=data.get('id'),
            course_id=data['course_id'],
            student_number=data['student_number'],
            class_number=data.get('class_number'),
            student_name=data['student_name'],
            note1=data.get('note1'),
            note2=data.get('note2'),
            note3=data.get('note3'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
