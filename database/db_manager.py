import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """データベース接続・操作を管理するクラス"""
    
    def __init__(self, db_path: str = "data/database.db"):
        """
        初期化とデータベース接続
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
        self.create_tables()
    
    def _connect(self):
        """データベースに接続"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self.connection.row_factory = sqlite3.Row
            # 外部キー制約を有効化
            self.connection.execute("PRAGMA foreign_keys = ON")
            logger.info(f"データベースに接続しました: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"データベース接続エラー: {e}")
            raise
    
    def create_tables(self):
        """テーブルを作成"""
        try:
            init_sql_path = Path(__file__).parent / "migrations" / "init_db.sql"
            with open(init_sql_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            self.connection.executescript(sql_script)
            self.connection.commit()
            logger.info("テーブルを作成しました")
        except Exception as e:
            logger.error(f"テーブル作成エラー: {e}")
            raise
    
    def backup_database(self, backup_dir: str = "data/backups") -> str:
        """
        データベースをバックアップ
        
        Args:
            backup_dir: バックアップ保存先ディレクトリ
            
        Returns:
            バックアップファイルのパス
        """
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"database_backup_{timestamp}.db"
            
            shutil.copy2(self.db_path, backup_file)
            logger.info(f"データベースをバックアップしました: {backup_file}")
            
            return str(backup_file)
        except Exception as e:
            logger.error(f"バックアップエラー: {e}")
            raise
    
    def execute_query(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """
        クエリを実行
        
        Args:
            query: SQL クエリ
            params: パラメータ
            
        Returns:
            カーソルオブジェクト
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            logger.error(f"クエリ実行エラー: {e}\nQuery: {query}\nParams: {params}")
            raise
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """
        全レコードを取得
        
        Args:
            query: SQL クエリ
            params: パラメータ
            
        Returns:
            レコードのリスト
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """
        1レコードを取得
        
        Args:
            query: SQL クエリ
            params: パラメータ
            
        Returns:
            レコード（存在しない場合はNone）
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchone()
    
    def commit(self):
        """トランザクションをコミット"""
        try:
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"コミットエラー: {e}")
            raise
    
    def rollback(self):
        """トランザクションをロールバック"""
        try:
            self.connection.rollback()
            logger.warning("トランザクションをロールバックしました")
        except sqlite3.Error as e:
            logger.error(f"ロールバックエラー: {e}")
            raise
    
    def close(self):
        """データベース接続を閉じる"""
        if self.connection:
            self.connection.close()
            logger.info("データベース接続を閉じました")
    
    def __enter__(self):
        """コンテキストマネージャー: with文で使用"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー: 終了時処理"""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()
