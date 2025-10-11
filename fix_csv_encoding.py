#!/usr/bin/env python3
"""CSVエクスポートのエンコーディングをUTF-8に統一する修正スクリプト"""

import re
from pathlib import Path


def fix_csv_encoding_in_file(file_path: Path) -> bool:
    """
    ファイル内のCSVエクスポート処理のエンコーディングをUTF-8に統一
    
    Args:
        file_path: 修正対象のファイルパス
        
    Returns:
        修正が行われた場合はTrue
    """
    try:
        # ファイル読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # パターン1: open(..., encoding='utf-8-sig', ...) を open(..., encoding='utf-8', ...) に変更
        content = re.sub(
            r"open\(([^)]*?)encoding=['\"]utf-8-sig['\"]([^)]*?)\)",
            r"open(\1encoding='utf-8'\2)",
            content
        )
        
        # パターン2: encoding='utf-8-sig' を encoding='utf-8' に変更（一般）
        content = re.sub(
            r"encoding=['\"]utf-8-sig['\"]",
            r"encoding='utf-8'",
            content
        )
        
        # 変更があった場合のみ書き込み
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"❌ エラー: {file_path}: {e}")
        return False


def main():
    """メイン処理"""
    print("=" * 70)
    print("CSVエクスポートのエンコーディング修正スクリプト")
    print("=" * 70)
    print()
    
    # 修正対象ファイルのリスト
    target_files = [
        "database/repositories/course_repository.py",
        "database/repositories/student_repository.py",
        "database/repositories/grade_repository.py",
    ]
    
    project_root = Path(__file__).parent
    modified_files = []
    skipped_files = []
    error_files = []
    
    print("📝 修正対象ファイル:")
    for file_path_str in target_files:
        print(f"  - {file_path_str}")
    print()
    
    # 各ファイルを処理
    for file_path_str in target_files:
        file_path = project_root / file_path_str
        
        if not file_path.exists():
            print(f"⚠️  ファイルが見つかりません: {file_path_str}")
            error_files.append(file_path_str)
            continue
        
        print(f"🔄 処理中: {file_path_str}")
        
        if fix_csv_encoding_in_file(file_path):
            print(f"✅ 修正完了: {file_path_str}")
            modified_files.append(file_path_str)
        else:
            print(f"⏭️  変更なし: {file_path_str}")
            skipped_files.append(file_path_str)
        
        print()
    
    # 結果サマリー
    print("=" * 70)
    print("修正結果サマリー")
    print("=" * 70)
    print(f"✅ 修正されたファイル: {len(modified_files)}件")
    for file_path in modified_files:
        print(f"  - {file_path}")
    print()
    
    print(f"⏭️  変更なし: {len(skipped_files)}件")
    for file_path in skipped_files:
        print(f"  - {file_path}")
    print()
    
    if error_files:
        print(f"❌ エラー: {len(error_files)}件")
        for file_path in error_files:
            print(f"  - {file_path}")
        print()
    
    print("=" * 70)
    print("修正内容:")
    print("  encoding='utf-8-sig' → encoding='utf-8'")
    print()
    print("⚠️  注意:")
    print("  - UTF-8（BOM無し）で保存されます")
    print("  - Excelで開く場合は、インポート時に文字コードを指定してください")
    print("  - または、Excel用にBOM付きUTF-8が必要な場合は utf-8-sig を使用してください")
    print("=" * 70)


if __name__ == "__main__":
    main()
