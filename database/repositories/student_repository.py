from typing import List, Optional
import csv
import logging
from pathlib import Path
from datetime import datetime

from database.db_manager import DatabaseManager
from models.student import Student

logger = logging.getLogger(__name__)




class StudentRepository:
    """生徒データのCRUD操作を行うリポジトリ"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初期化
        
        Args:
            db_manager: データベースマネージャー
        """
        self.db = db_manager
    
    def get_students_by_course(self, course_id: int) -> List[Student]:
        """
        講座IDで生徒を取得
        
        Args:
            course_id: 講座ID
            
        Returns:
            生徒のリスト
        """
        try:
            query = """
                SELECT id, course_id, student_number, class_number, student_name,
                       note1, note2, note3, created_at, updated_at
                FROM course_students
                WHERE course_id = ?
                ORDER BY student_number
            """
            rows = self.db.fetch_all(query, (course_id,))
            return [Student(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"生徒取得エラー (講座ID: {course_id}): {e}")
            raise
    
    def get_student_by_number(self, course_id: int, student_number: str) -> Optional[Student]:
        """
        講座IDと生徒番号で生徒を取得
        
        Args:
            course_id: 講座ID
            student_number: 生徒番号
            
        Returns:
            生徒オブジェクト（存在しない場合はNone）
        """
        try:
            query = """
                SELECT id, course_id, student_number, class_number, student_name,
                       note1, note2, note3, created_at, updated_at
                FROM course_students
                WHERE course_id = ? AND student_number = ?
            """
            row = self.db.fetch_one(query, (course_id, student_number))
            return Student(**dict(row)) if row else None
        except Exception as e:
            logger.error(f"生徒取得エラー (講座ID: {course_id}, 番号: {student_number}): {e}")
            raise
    
    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """
        IDで生徒を取得
        
        Args:
            student_id: 生徒ID
            
        Returns:
            生徒オブジェクト（存在しない場合はNone）
        """
        try:
            query = """
                SELECT id, course_id, student_number, class_number, student_name,
                       note1, note2, note3, created_at, updated_at
                FROM course_students
                WHERE id = ?
            """
            row = self.db.fetch_one(query, (student_id,))
            return Student(**dict(row)) if row else None
        except Exception as e:
            logger.error(f"生徒取得エラー (ID: {student_id}): {e}")
            raise
    
    def create_student(self, student: Student) -> int:
        """
        生徒を作成
        
        Args:
            student: 生徒オブジェクト
            
        Returns:
            作成された生徒のID
        """
        try:
            query = """
                INSERT INTO course_students 
                (course_id, student_number, class_number, student_name, 
                 note1, note2, note3)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor = self.db.execute_query(
                query,
                (student.course_id, student.student_number, student.class_number,
                 student.student_name, student.note1, student.note2, student.note3)
            )
            self.db.commit()
            logger.info(f"生徒を作成しました: {student.student_name}")
            return cursor.lastrowid
        except Exception as e:
            self.db.rollback()
            logger.error(f"生徒作成エラー: {e}")
            raise
    
    def update_student(self, student: Student):
        """
        生徒を更新
        
        Args:
            student: 生徒オブジェクト
        """
        try:
            query = """
                UPDATE course_students
                SET student_number = ?, class_number = ?, student_name = ?,
                    note1 = ?, note2 = ?, note3 = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            self.db.execute_query(
                query,
                (student.student_number, student.class_number, student.student_name,
                 student.note1, student.note2, student.note3, student.id)
            )
            self.db.commit()
            logger.info(f"生徒を更新しました: {student.student_name}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"生徒更新エラー: {e}")
            raise
    
    def delete_student(self, student_id: int):
        """
        生徒を削除
        
        Args:
            student_id: 生徒ID
        """
        try:
            query = "DELETE FROM course_students WHERE id = ?"
            self.db.execute_query(query, (student_id,))
            self.db.commit()
            logger.info(f"生徒を削除しました (ID: {student_id})")
        except Exception as e:
            self.db.rollback()
            logger.error(f"生徒削除エラー: {e}")
            raise
    
    def import_from_csv_with_replacement(self, csv_path: str, course_id: Optional[int] = None) -> dict:
        """
        CSVファイルから生徒を一括インポート（差し替え式）
        
        Args:
            csv_path: CSVファイルのパス
            course_id: 講座ID（指定時はその講座のみ差し替え、Noneの場合は全体）
            
        Returns:
            インポート結果（deleted, created, errors, backup_path）
        """
        result = {'deleted': 0, 'created': 0, 'errors': [], 'backup_path': None}
        
        try:
            # Step 1: 自動バックアップ作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 講座名を取得（バックアップファイル名用）
            course_name = "all"
            if course_id:
                from database.repositories.course_repository import CourseRepository
                course_repo = CourseRepository(self.db)
                course = course_repo.get_course_by_id(course_id)
                if course:
                    course_name = course.course_name
            
            backup_dir = Path("data/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"before_import_students_{course_name}_{timestamp}.csv"
            
            # バックアップ作成
            self.export_to_csv(str(backup_path), course_id)
            result['backup_path'] = str(backup_path)
            logger.info(f"自動バックアップ作成: {backup_path}")
            
            # Step 2: CSVデータを読み込み
            csv_data = []
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        course_name_csv = row.get('course_name', '').strip()
                        student_number = row.get('student_number', '').strip()
                        student_name = row.get('student_name', '').strip()
                        
                        if not all([course_name_csv, student_number, student_name]):
                            result['errors'].append(f"行 {row_num}: 必須項目が空です")
                            continue
                        
                        # 講座IDを取得
                        course_query = "SELECT course_id FROM courses WHERE course_name = ?"
                        course_row = self.db.fetch_one(course_query, (course_name_csv,))
                        
                        if not course_row:
                            result['errors'].append(f"行 {row_num}: 講座が見つかりません: {course_name_csv}")
                            continue
                        
                        csv_course_id = course_row['course_id']
                        
                        # course_id指定時は、その講座のみを対象
                        if course_id and csv_course_id != course_id:
                            continue
                        
                        student_data = {
                            'course_id': csv_course_id,
                            'student_number': student_number,
                            'class_number': row.get('class_number', '').strip() or None,
                            'student_name': student_name,
                            'note1': row.get('note1', '').strip() or None,
                            'note2': row.get('note2', '').strip() or None,
                            'note3': row.get('note3', '').strip() or None
                        }
                        
                        csv_data.append(student_data)
                    
                    except Exception as e:
                        result['errors'].append(f"行 {row_num}: {str(e)}")
                        logger.error(f"CSVインポートエラー (行 {row_num}): {e}")
            
            if not csv_data:
                logger.warning("CSVに有効なデータがありません")
                return result
            
            # Step 3: トランザクション内で削除と挿入を実行
            if course_id:
                # 指定講座のみ削除
                delete_query = "DELETE FROM course_students WHERE course_id = ?"
                cursor = self.db.execute_query(delete_query, (course_id,))
            else:
                # 全生徒を削除
                delete_query = "DELETE FROM course_students"
                cursor = self.db.execute_query(delete_query)
            
            result['deleted'] = cursor.rowcount
            logger.info(f"削除完了: {result['deleted']}件")
            
            # Step 4: CSVデータを挿入
            insert_query = """
                INSERT INTO course_students 
                (course_id, student_number, class_number, student_name, note1, note2, note3)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            for student_data in csv_data:
                try:
                    self.db.execute_query(
                        insert_query,
                        (student_data['course_id'], student_data['student_number'],
                         student_data['class_number'], student_data['student_name'],
                         student_data['note1'], student_data['note2'], student_data['note3'])
                    )
                    result['created'] += 1
                except Exception as e:
                    error_msg = f"挿入エラー: 講座ID={student_data['course_id']}, 生徒番号={student_data['student_number']}: {str(e)}"
                    result['errors'].append(error_msg)
                    logger.error(error_msg)
            
            # Step 5: コミット
            self.db.commit()
            
            logger.info(f"CSV差し替えインポート完了: 削除={result['deleted']}, "
                       f"作成={result['created']}, エラー={len(result['errors'])}")
            return result
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"CSVインポートエラー: {e}")
            result['errors'].append(f"致命的エラー: {str(e)}")
            raise

    def export_to_csv(self, csv_path: str, course_id: Optional[int] = None):
        """
        生徒をCSVファイルにエクスポート
        
        Args:
            csv_path: CSVファイルのパス
            course_id: 講座ID（指定しない場合は全生徒）
        """
        try:
            if course_id:
                query = """
                    SELECT c.course_name, cs.student_number, cs.class_number,
                           cs.student_name, cs.note1, cs.note2, cs.note3
                    FROM course_students cs
                    JOIN courses c ON cs.course_id = c.course_id
                    WHERE cs.course_id = ?
                    ORDER BY cs.student_number
                """
                rows = self.db.fetch_all(query, (course_id,))
            else:
                query = """
                    SELECT c.course_name, cs.student_number, cs.class_number,
                           cs.student_name, cs.note1, cs.note2, cs.note3
                    FROM course_students cs
                    JOIN courses c ON cs.course_id = c.course_id
                    ORDER BY c.course_name, cs.student_number
                """
                rows = self.db.fetch_all(query)
            
            Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                fieldnames = ['course_name', 'student_number', 'class_number',
                            'student_name', 'note1', 'note2', 'note3']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in rows:
                    writer.writerow({
                        'course_name': row['course_name'],
                        'student_number': row['student_number'],
                        'class_number': row['class_number'] or '',
                        'student_name': row['student_name'],
                        'note1': row['note1'] or '',
                        'note2': row['note2'] or '',
                        'note3': row['note3'] or ''
                    })
            
            logger.info(f"CSVエクスポート完了: {len(rows)}件 -> {csv_path}")
        
        except Exception as e:
            logger.error(f"CSVエクスポートエラー: {e}")
            raise
