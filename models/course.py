from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Course:
    """講座モデル"""
    course_id: Optional[int]
    course_name: str
    note1: Optional[str] = None
    note2: Optional[str] = None
    note3: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'note1': self.note1,
            'note2': self.note2,
            'note3': self.note3,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Course':
        """辞書形式から生成"""
        return cls(
            course_id=data.get('course_id'),
            course_name=data['course_name'],
            note1=data.get('note1'),
            note2=data.get('note2'),
            note3=data.get('note3'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
