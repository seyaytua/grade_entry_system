import csv
from typing import List, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CSVHandler:
    """CSV入出力処理を行うユーティリティクラス"""
    
    @staticmethod
    def read_csv(file_path: str) -> List[Dict]:
        """
        CSVファイルを読み込む（UTF-8対応）
        
        Args:
            file_path: CSVファイルのパス
            
        Returns:
            辞書のリスト（各行がキー・バリューのペア）
        """
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            
            logger.info(f"CSVファイルを読み込みました: {file_path} ({len(data)}行)")
            return data
        except FileNotFoundError:
            logger.error(f"ファイルが見つかりません: {file_path}")
            raise
        except Exception as e:
            logger.error(f"CSV読み込みエラー: {e}")
            raise
    
    @staticmethod
    def write_csv(file_path: str, data: List[Dict], headers: List[str]):
        """
        CSVファイルに書き込む（UTF-8 BOM付き）
        
        Args:
            file_path: CSVファイルのパス
            data: 書き込むデータ（辞書のリスト）
            headers: ヘッダー（列名のリスト）
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"CSVファイルに書き込みました: {file_path} ({len(data)}行)")
        except Exception as e:
            logger.error(f"CSV書き込みエラー: {e}")
            raise
    
    @staticmethod
    def validate_csv_format(data: List[Dict], required_fields: List[str]) -> bool:
        """
        CSVフォーマットを検証
        
        Args:
            data: 検証するデータ
            required_fields: 必須フィールドのリスト
            
        Returns:
            検証結果（True: 正常, False: エラー）
        """
        if not data:
            logger.warning("CSVデータが空です")
            return False
        
        # ヘッダーの確認
        headers = data[0].keys()
        missing_fields = [field for field in required_fields if field not in headers]
        
        if missing_fields:
            logger.error(f"必須フィールドが不足しています: {missing_fields}")
            return False
        
        logger.info("CSVフォーマット検証: OK")
        return True
