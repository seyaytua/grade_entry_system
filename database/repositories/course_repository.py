from typing import List, Optional
import csv
import logging
from pathlib import Path
from datetime import datetime

from database.db_manager import DatabaseManager
from models.course import Course

logger = logging.getLogger(__name__)




class CourseRepository:
    """講座データのCRUD操作を行うリポジトリ"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初期化
        
        Args:
            db_manager: データベースマネージャー
        """
        self.db = db_manager
    
    def get_all_courses(self) -> List[Course]:
        """
        全講座を取得
        
        Returns:
            講座のリスト
        """
        try:
            query = """
                SELECT course_id, course_name, note1, note2, note3, 
                       created_at, updated_at
                FROM courses
                ORDER BY course_name
            """
            rows = self.db.fetch_all(query)
            return [Course(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"講座取得エラー: {e}")
            raise
    
    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """
        講座IDで講座を取得
        
        Args:
            course_id: 講座ID
            
        Returns:
            講座オブジェクト（存在しない場合はNone）
        """
        try:
            query = """
                SELECT course_id, course_name, note1, note2, note3,
                       created_at, updated_at
                FROM courses
                WHERE course_id = ?
            """
            row = self.db.fetch_one(query, (course_id,))
            return Course(**dict(row)) if row else None
        except Exception as e:
            logger.error(f"講座取得エラー (ID: {course_id}): {e}")
            raise
    
    def get_course_by_name(self, course_name: str) -> Optional[Course]:
        """
        講座名で講座を取得
        
        Args:
            course_name: 講座名
            
        Returns:
            講座オブジェクト（存在しない場合はNone）
        """
        try:
            query = """
                SELECT course_id, course_name, note1, note2, note3,
                       created_at, updated_at
                FROM courses
                WHERE course_name = ?
            """
            row = self.db.fetch_one(query, (course_name,))
            return Course(**dict(row)) if row else None
        except Exception as e:
            logger.error(f"講座取得エラー (名前: {course_name}): {e}")
            raise
    
    def create_course(self, course: Course) -> int:
        """
        講座を作成
        
        Args:
            course: 講座オブジェクト
            
        Returns:
            作成された講座のID
        """
        try:
            query = """
                INSERT INTO courses (course_name, note1, note2, note3)
                VALUES (?, ?, ?, ?)
            """
            cursor = self.db.execute_query(
                query,
                (course.course_name, course.note1, course.note2, course.note3)
            )
            self.db.commit()
            logger.info(f"講座を作成しました: {course.course_name}")
            return cursor.lastrowid
        except Exception as e:
            self.db.rollback()
            logger.error(f"講座作成エラー: {e}")
            raise
    
    def update_course(self, course: Course):
        """
        講座を更新
        
        Args:
            course: 講座オブジェクト
        """
        try:
            query = """
                UPDATE courses
                SET course_name = ?, note1 = ?, note2 = ?, note3 = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE course_id = ?
            """
            self.db.execute_query(
                query,
                (course.course_name, course.note1, course.note2, 
                 course.note3, course.course_id)
            )
            self.db.commit()
            logger.info(f"講座を更新しました: {course.course_name}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"講座更新エラー: {e}")
            raise
    
    def delete_course(self, course_id: int):
        """
        講座を削除（カスケード削除により関連データも削除）
        
        Args:
            course_id: 講座ID
        """
        try:
            query = "DELETE FROM courses WHERE course_id = ?"
            self.db.execute_query(query, (course_id,))
            self.db.commit()
            logger.info(f"講座を削除しました (ID: {course_id})")
        except Exception as e:
            self.db.rollback()
            logger.error(f"講座削除エラー: {e}")
            raise
    
    def import_from_csv_with_replacement(self, csv_path: str) -> dict:
        """
        CSVファイルから講座を一括インポート（差し替え式）
        
        Args:
            csv_path: CSVファイルのパス
            
        Returns:
            インポート結果（deleted, created, errors, backup_path）
        """
        result = {'deleted': 0, 'created': 0, 'errors': [], 'backup_path': None}
        
        try:
            # Step 1: 自動バックアップ作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path("data/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"before_import_courses_{timestamp}.csv"
            
            # 既存の全講座をバックアップ
            self.export_to_csv(str(backup_path))
            result['backup_path'] = str(backup_path)
            logger.info(f"自動バックアップ作成: {backup_path}")
            
            # Step 2: CSVデータを読み込み
            csv_data = []
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        course_name = row.get('course_name', '').strip()
                        if not course_name:
                            result['errors'].append(f"行 {row_num}: 講座名が空です")
                            continue
                        
                        course_data = {
                            'course_name': course_name,
                            'note1': row.get('note1', '').strip() or None,
                            'note2': row.get('note2', '').strip() or None,
                            'note3': row.get('note3', '').strip() or None
                        }
                        
                        csv_data.append(course_data)
                    
                    except Exception as e:
                        result['errors'].append(f"行 {row_num}: {str(e)}")
                        logger.error(f"CSVインポートエラー (行 {row_num}): {e}")
            
            if not csv_data:
                logger.warning("CSVに有効なデータがありません")
                return result
            
            # Step 3: トランザクション内で削除と挿入を実行
            # 全講座を削除
            delete_query = "DELETE FROM courses"
            cursor = self.db.execute_query(delete_query)
            result['deleted'] = cursor.rowcount
            logger.info(f"削除完了: {result['deleted']}件")
            
            # Step 4: CSVデータを挿入
            insert_query = """
                INSERT INTO courses (course_name, note1, note2, note3)
                VALUES (?, ?, ?, ?)
            """
            
            for course_data in csv_data:
                try:
                    self.db.execute_query(
                        insert_query,
                        (course_data['course_name'], course_data['note1'],
                         course_data['note2'], course_data['note3'])
                    )
                    result['created'] += 1
                except Exception as e:
                    error_msg = f"挿入エラー: 講座名={course_data['course_name']}: {str(e)}"
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

    def export_to_csv(self, csv_path: str):
        """
        講座をCSVファイルにエクスポート
        
        Args:
            csv_path: CSVファイルのパス
        """
        try:
            courses = self.get_all_courses()
            
            Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                fieldnames = ['course_name', 'note1', 'note2', 'note3']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for course in courses:
                    writer.writerow({
                        'course_name': course.course_name,
                        'note1': course.note1 or '',
                        'note2': course.note2 or '',
                        'note3': course.note3 or ''
                    })
            
            logger.info(f"CSVエクスポート完了: {len(courses)}件 -> {csv_path}")
        
        except Exception as e:
            logger.error(f"CSVエクスポートエラー: {e}")
            raise
