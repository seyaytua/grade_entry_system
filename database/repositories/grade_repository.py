from typing import List, Optional, Dict
import csv
import logging
from pathlib import Path
from datetime import datetime

from database.db_manager import DatabaseManager
from models.grade import Grade, GradeListItem

logger = logging.getLogger(__name__)


class GradeRepository:
    """成績データのCRUD操作を行うリポジトリ"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初期化
        
        Args:
            db_manager: データベースマネージャー
        """
        self.db = db_manager
    
    def get_grades_by_course_date(self, course_id: int, entry_date: str) -> List[Grade]:
        """
        講座IDと授業日で成績を取得
        
        Args:
            course_id: 講座ID
            entry_date: 授業日 (YYYY-MM-DD)
            
        Returns:
            成績のリスト
        """
        try:
            query = """
                SELECT id, course_id, entry_date, student_number,
                       grade1, grade2, grade3, grade4, grade5, grade6,
                       note1, note2, created_at, updated_at
                FROM grade_entries
                WHERE course_id = ? AND entry_date = ?
                ORDER BY student_number
            """
            rows = self.db.fetch_all(query, (course_id, entry_date))
            return [Grade(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"成績取得エラー (講座ID: {course_id}, 日付: {entry_date}): {e}")
            raise
    
    def get_grade_list(self, filters: Optional[Dict] = None) -> List[GradeListItem]:
        """
        成績一覧を取得（フィルタ・ソート付き）
        
        Args:
            filters: フィルタ条件の辞書
                - course_ids: 講座IDのリスト
                - start_date: 開始日
                - end_date: 終了日
                - student_number: 生徒番号（部分一致）
                - class_number: クラス番号
                - sort_by: ソート列名
                - sort_order: 'ASC' or 'DESC'
                
        Returns:
            成績一覧のリスト
        """
        try:
            query = "SELECT * FROM grade_list_view WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('course_ids'):
                    placeholders = ','.join('?' * len(filters['course_ids']))
                    query += f" AND course_id IN ({placeholders})"
                    params.extend(filters['course_ids'])
                
                if filters.get('start_date'):
                    query += " AND entry_date >= ?"
                    params.append(filters['start_date'])
                
                if filters.get('end_date'):
                    query += " AND entry_date <= ?"
                    params.append(filters['end_date'])
                
                if filters.get('student_number'):
                    query += " AND student_number LIKE ?"
                    params.append(f"%{filters['student_number']}%")
                
                if filters.get('class_number'):
                    query += " AND class_number = ?"
                    params.append(filters['class_number'])
                
                # ソート
                sort_by = filters.get('sort_by', 'entry_date')
                sort_order = filters.get('sort_order', 'ASC')
                query += f" ORDER BY {sort_by} {sort_order}"
            
            rows = self.db.fetch_all(query, tuple(params))
            return [GradeListItem.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"成績一覧取得エラー: {e}")
            raise
    
    def create_or_update_grade(self, grade: Grade) -> int:
        """
        成績を作成または更新（UPSERT）
        
        Args:
            grade: 成績オブジェクト
            
        Returns:
            成績ID
        """
        try:
            query = """
                INSERT INTO grade_entries 
                (course_id, entry_date, student_number, grade1, grade2, grade3,
                 grade4, grade5, grade6, note1, note2)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(course_id, entry_date, student_number)
                DO UPDATE SET
                    grade1 = excluded.grade1,
                    grade2 = excluded.grade2,
                    grade3 = excluded.grade3,
                    grade4 = excluded.grade4,
                    grade5 = excluded.grade5,
                    grade6 = excluded.grade6,
                    note1 = excluded.note1,
                    note2 = excluded.note2,
                    updated_at = CURRENT_TIMESTAMP
            """
            cursor = self.db.execute_query(
                query,
                (grade.course_id, grade.entry_date, grade.student_number,
                 grade.grade1, grade.grade2, grade.grade3,
                 grade.grade4, grade.grade5, grade.grade6,
                 grade.note1, grade.note2)
            )
            self.db.commit()
            
            # 作成または更新されたIDを取得
            if cursor.lastrowid > 0:
                grade_id = cursor.lastrowid
            else:
                # 更新の場合は既存IDを取得
                id_query = """
                    SELECT id FROM grade_entries
                    WHERE course_id = ? AND entry_date = ? AND student_number = ?
                """
                row = self.db.fetch_one(
                    id_query,
                    (grade.course_id, grade.entry_date, grade.student_number)
                )
                grade_id = row['id'] if row else None
            
            logger.info(f"成績を保存しました (ID: {grade_id})")
            return grade_id
        except Exception as e:
            self.db.rollback()
            logger.error(f"成績保存エラー: {e}")
            raise
    
    def delete_grade(self, grade_id: int):
        """
        成績を削除
        
        Args:
            grade_id: 成績ID
        """
        try:
            query = "DELETE FROM grade_entries WHERE id = ?"
            self.db.execute_query(query, (grade_id,))
            self.db.commit()
            logger.info(f"成績を削除しました (ID: {grade_id})")
        except Exception as e:
            self.db.rollback()
            logger.error(f"成績削除エラー: {e}")
            raise
    
    def delete_grades_by_filter(self, filters: Dict) -> int:
        """
        フィルタ条件に合致する成績を削除
        
        Args:
            filters: フィルタ条件
            
        Returns:
            削除件数
        """
        try:
            query = "DELETE FROM grade_entries WHERE 1=1"
            params = []
            
            if filters.get('course_ids'):
                placeholders = ','.join('?' * len(filters['course_ids']))
                query += f" AND course_id IN ({placeholders})"
                params.extend(filters['course_ids'])
            
            if filters.get('start_date'):
                query += " AND entry_date >= ?"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                query += " AND entry_date <= ?"
                params.append(filters['end_date'])
            
            cursor = self.db.execute_query(query, tuple(params))
            deleted_count = cursor.rowcount
            
            logger.info(f"フィルタ条件で成績を削除しました ({deleted_count}件)")
            return deleted_count
        except Exception as e:
            logger.error(f"成績削除エラー: {e}")
            raise
    
    def export_to_csv(self, csv_path: str, filters: Optional[Dict] = None):
        """
        成績をCSVファイルにエクスポート
        
        Args:
            csv_path: CSVファイルのパス
            filters: フィルタ条件
        """
        try:
            grades = self.get_grade_list(filters)
            
            Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = [
                    'course_name', 'entry_date', 'student_number', 'student_name',
                    'class_number', 'grade1', 'grade2', 'grade3', 'grade4',
                    'grade5', 'grade6', 'note1', 'note2'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for grade in grades:
                    writer.writerow({
                        'course_name': grade.course_name,
                        'entry_date': grade.entry_date,
                        'student_number': grade.student_number,
                        'student_name': grade.student_name,
                        'class_number': grade.class_number or '',
                        'grade1': grade.grade1 if grade.grade1 is not None else '',
                        'grade2': grade.grade2 if grade.grade2 is not None else '',
                        'grade3': grade.grade3 if grade.grade3 is not None else '',
                        'grade4': grade.grade4 if grade.grade4 is not None else '',
                        'grade5': grade.grade5 if grade.grade5 is not None else '',
                        'grade6': grade.grade6 if grade.grade6 is not None else '',
                        'note1': grade.note1 or '',
                        'note2': grade.note2 or ''
                    })
            
            logger.info(f"CSVエクスポート完了: {len(grades)}件 -> {csv_path}")
        except Exception as e:
            logger.error(f"CSVエクスポートエラー: {e}")
            raise
    
    def import_from_csv_with_replacement(self, csv_path: str, filters: Dict) -> dict:
        """
        CSVファイルから成績を一括インポート（差し替え式）
        
        Args:
            csv_path: CSVファイルのパス
            filters: 差し替え範囲のフィルタ条件
            
        Returns:
            インポート結果（deleted, created, errors, backup_path）
        """
        result = {'deleted': 0, 'created': 0, 'errors': [], 'backup_path': None}
        
        try:
            # Step 1: 自動バックアップ作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 講座名を取得（バックアップファイル名用）
            course_name = "all"
            if filters.get('course_ids') and len(filters['course_ids']) == 1:
                from database.repositories.course_repository import CourseRepository
                course_repo = CourseRepository(self.db)
                course = course_repo.get_course_by_id(filters['course_ids'][0])
                if course:
                    course_name = course.course_name
            
            backup_dir = Path("data/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"before_import_{course_name}_{timestamp}.csv"
            
            # バックアップ作成
            self.export_to_csv(str(backup_path), filters)
            result['backup_path'] = str(backup_path)
            logger.info(f"自動バックアップ作成: {backup_path}")
            
            # Step 2: CSVデータを読み込み（先に読み込んでバリデーション）
            csv_data = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        course_name_csv = row.get('course_name', '').strip()
                        entry_date_raw = row.get('entry_date', '').strip()
                        student_number = row.get('student_number', '').strip()
                        
                        if not all([course_name_csv, entry_date_raw, student_number]):
                            result['errors'].append(f"行 {row_num}: 必須項目が空です")
                            continue
                        
                        # 日付フォーマットを統一（YYYY-MM-DD形式に変換）
                        entry_date = self._normalize_date(entry_date_raw)
                        if not entry_date:
                            result['errors'].append(f"行 {row_num}: 日付フォーマットが不正です: {entry_date_raw}")
                            continue
                        
                        # 講座IDを取得
                        course_query = "SELECT course_id FROM courses WHERE course_name = ?"
                        course_row = self.db.fetch_one(course_query, (course_name_csv,))
                        
                        if not course_row:
                            result['errors'].append(f"行 {row_num}: 講座が見つかりません: {course_name_csv}")
                            continue
                        
                        course_id = course_row['course_id']
                        
                        # 成績データの準備
                        def parse_value(val, type_func):
                            val = val.strip() if val else ''
                            return type_func(val) if val else None
                        
                        grade_data = {
                            'course_id': course_id,
                            'entry_date': entry_date,
                            'student_number': student_number,
                            'grade1': parse_value(row.get('grade1', ''), int),
                            'grade2': parse_value(row.get('grade2', ''), int),
                            'grade3': parse_value(row.get('grade3', ''), int),
                            'grade4': parse_value(row.get('grade4', ''), float),
                            'grade5': parse_value(row.get('grade5', ''), float),
                            'grade6': parse_value(row.get('grade6', ''), float),
                            'note1': row.get('note1', '').strip() or None,
                            'note2': row.get('note2', '').strip() or None
                        }
                        
                        csv_data.append(grade_data)
                    
                    except ValueError as e:
                        result['errors'].append(f"行 {row_num}: 数値変換エラー: {str(e)}")
                    except Exception as e:
                        result['errors'].append(f"行 {row_num}: {str(e)}")
                        logger.error(f"CSVインポートエラー (行 {row_num}): {e}")
            
            # エラーが多い場合は警告
            if len(result['errors']) > 0:
                logger.warning(f"CSVバリデーションエラー: {len(result['errors'])}件")
            
            # CSVにデータがない場合
            if not csv_data:
                logger.warning("CSVに有効なデータがありません")
                return result
            
            # Step 3: トランザクション内で削除と挿入を実行
            # 削除クエリの構築
            delete_query = "DELETE FROM grade_entries WHERE 1=1"
            delete_params = []
            
            if filters.get('course_ids'):
                placeholders = ','.join('?' * len(filters['course_ids']))
                delete_query += f" AND course_id IN ({placeholders})"
                delete_params.extend(filters['course_ids'])
            
            if filters.get('start_date'):
                delete_query += " AND entry_date >= ?"
                delete_params.append(filters['start_date'])
            
            if filters.get('end_date'):
                delete_query += " AND entry_date <= ?"
                delete_params.append(filters['end_date'])
            
            logger.info(f"削除クエリ: {delete_query}")
            logger.info(f"削除パラメータ: {delete_params}")
            
            # 削除実行
            cursor = self.db.execute_query(delete_query, tuple(delete_params))
            result['deleted'] = cursor.rowcount
            logger.info(f"削除完了: {result['deleted']}件")
            
            # Step 4: CSVデータを挿入
            insert_query = """
                INSERT INTO grade_entries 
                (course_id, entry_date, student_number, grade1, grade2, grade3,
                 grade4, grade5, grade6, note1, note2)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for grade_data in csv_data:
                try:
                    self.db.execute_query(
                        insert_query,
                        (grade_data['course_id'], grade_data['entry_date'], grade_data['student_number'],
                         grade_data['grade1'], grade_data['grade2'], grade_data['grade3'],
                         grade_data['grade4'], grade_data['grade5'], grade_data['grade6'],
                         grade_data['note1'], grade_data['note2'])
                    )
                    result['created'] += 1
                except Exception as e:
                    error_msg = f"挿入エラー: 講座ID={grade_data['course_id']}, 日付={grade_data['entry_date']}, 生徒={grade_data['student_number']}: {str(e)}"
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
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        日付文字列を YYYY-MM-DD 形式に統一
        
        Args:
            date_str: 日付文字列 (YYYY/M/D, YYYY-M-D, YYYY/MM/DD, YYYY-MM-DD など)
            
        Returns:
            YYYY-MM-DD形式の日付文字列、または None
        """
        from datetime import datetime
        
        # 対応する日付フォーマット
        formats = [
            "%Y/%m/%d",
            "%Y-%m-%d",
            "%Y/%#m/%#d",  # Windows
            "%Y/%-m/%-d",  # Unix/Mac
            "%Y-%#m-%#d",  # Windows
            "%Y-%-m-%-d",  # Unix/Mac
        ]
        
        # スラッシュをハイフンに置換して試す
        date_str_normalized = date_str.replace('/', '-')
        
        # 日付パース
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except:
                pass
        
        # 単純な置換で試す（YYYY/M/D -> YYYY-MM-DD）
        try:
            parts = date_str_normalized.split('-')
            if len(parts) == 3:
                year, month, day = parts
                return f"{year:0>4}-{month:0>2}-{day:0>2}"
        except:
            pass
        
        return None

    def import_from_csv(self, csv_path: str) -> dict:
        """
        CSVファイルから成績を一括インポート（UPSERT方式・旧仕様）
        
        Args:
            csv_path: CSVファイルのパス
            
        Returns:
            インポート結果（created, updated, errors）
        """
        result = {'created': 0, 'updated': 0, 'errors': []}
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        course_name = row.get('course_name', '').strip()
                        entry_date = row.get('entry_date', '').strip()
                        student_number = row.get('student_number', '').strip()
                        
                        if not all([course_name, entry_date, student_number]):
                            result['errors'].append(f"行 {row_num}: 必須項目が空です")
                            continue
                        
                        # 講座IDを取得
                        course_query = "SELECT course_id FROM courses WHERE course_name = ?"
                        course_row = self.db.fetch_one(course_query, (course_name,))
                        
                        if not course_row:
                            result['errors'].append(f"行 {row_num}: 講座が見つかりません: {course_name}")
                            continue
                        
                        course_id = course_row['course_id']
                        
                        # 既存の成績を確認
                        existing_query = """
                            SELECT id FROM grade_entries
                            WHERE course_id = ? AND entry_date = ? AND student_number = ?
                        """
                        existing = self.db.fetch_one(
                            existing_query,
                            (course_id, entry_date, student_number)
                        )
                        
                        # 成績データの準備
                        def parse_value(val, type_func):
                            val = val.strip()
                            return type_func(val) if val else None
                        
                        grade = Grade(
                            id=existing['id'] if existing else None,
                            course_id=course_id,
                            entry_date=entry_date,
                            student_number=student_number,
                            grade1=parse_value(row.get('grade1', ''), int),
                            grade2=parse_value(row.get('grade2', ''), int),
                            grade3=parse_value(row.get('grade3', ''), int),
                            grade4=parse_value(row.get('grade4', ''), float),
                            grade5=parse_value(row.get('grade5', ''), float),
                            grade6=parse_value(row.get('grade6', ''), float),
                            note1=row.get('note1', '').strip() or None,
                            note2=row.get('note2', '').strip() or None
                        )
                        
                        self.create_or_update_grade(grade)
                        
                        if existing:
                            result['updated'] += 1
                        else:
                            result['created'] += 1
                    
                    except ValueError as e:
                        result['errors'].append(f"行 {row_num}: 数値変換エラー: {str(e)}")
                    except Exception as e:
                        result['errors'].append(f"行 {row_num}: {str(e)}")
                        logger.error(f"CSVインポートエラー (行 {row_num}): {e}")
            
            logger.info(f"CSVインポート完了: 作成={result['created']}, "
                       f"更新={result['updated']}, エラー={len(result['errors'])}")
            return result
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"CSVファイル読み込みエラー: {e}")
            raise
