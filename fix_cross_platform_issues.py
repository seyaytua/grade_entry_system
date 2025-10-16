#!/usr/bin/env python3
"""
クロスプラットフォーム対応の問題修正スクリプト
Linux環境でもビルドできるようにファイルパスとエンコーディングを修正
"""

import os
import sys
import shutil
from pathlib import Path

def fix_main_py():
    """main.pyのクロスプラットフォーム対応を改善"""
    main_file = Path("main.py")
    
    if not main_file.exists():
        print("main.pyが見つかりません")
        return False
    
    # main.pyの内容を読み取り
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Windowsでのパス問題を修正
    fixes = [
        # ログファイルパスの修正
        (
            "logging.FileHandler(project_root / 'grade_entry_system.log', encoding='utf-8')",
            "logging.FileHandler(str(project_root / 'grade_entry_system.log'), encoding='utf-8')"
        ),
    ]
    
    modified = False
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"修正: {old[:50]}...")
    
    if modified:
        # バックアップを作成
        shutil.copy2(main_file, f"{main_file}.backup")
        
        # 修正内容を書き込み
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("main.pyを修正しました")
    else:
        print("main.pyに修正が必要な箇所は見つかりませんでした")
    
    return True

def check_encoding_issues():
    """文字エンコーディングの問題をチェック"""
    print("文字エンコーディングをチェック中...")
    
    # プロジェクト内のPythonファイルをチェック
    py_files = list(Path(".").rglob("*.py"))
    
    encoding_issues = []
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # BOMの存在をチェック
                if content.startswith('\ufeff'):
                    encoding_issues.append(f"{py_file}: UTF-8 BOM検出")
        except UnicodeDecodeError as e:
            encoding_issues.append(f"{py_file}: エンコーディングエラー - {e}")
        except Exception as e:
            encoding_issues.append(f"{py_file}: その他のエラー - {e}")
    
    if encoding_issues:
        print("エンコーディングの問題が見つかりました:")
        for issue in encoding_issues:
            print(f"  - {issue}")
    else:
        print("エンコーディングの問題は見つかりませんでした")
    
    return len(encoding_issues) == 0

def check_import_issues():
    """インポートの問題をチェック"""
    print("インポートの問題をチェック中...")
    
    try:
        # 主要なモジュールのインポートをテスト
        import database
        import models
        import views
        import utils
        import config
        
        print("すべての基本モジュールのインポートに成功しました")
        return True
        
    except ImportError as e:
        print(f"インポートエラー: {e}")
        return False
    except Exception as e:
        print(f"その他のエラー: {e}")
        return False

def create_test_script():
    """テスト用のスクリプトを作成"""
    test_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
成績入力システム - インポートテスト
PyInstallerビルド前の基本動作確認用
\"\"\"

import sys
import traceback
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    \"\"\"すべてのモジュールのインポートをテスト\"\"\"
    modules_to_test = [
        'database',
        'database.db_manager',
        'database.repositories.course_repository',
        'database.repositories.student_repository', 
        'database.repositories.grade_repository',
        'models.course',
        'models.student',
        'models.grade',
        'models.split',
        'views.main_window',
        'views.grade_entry_view',
        'views.course_management_view',
        'views.student_management_view',
        'views.grade_list_view',
        'views.pdf_split_view',
        'views.widgets.image_preview_widget',
        'views.widgets.student_grade_card',
        'views.widgets.split_settings_dialog',
        'views.widgets.student_assignment_item',
        'utils.csv_handler',
        'utils.radio_button_helper',
        'utils.pdf_splitter',
        'config.settings',
    ]
    
    success_count = 0
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"✗ {module_name}: {e}")
            failed_imports.append((module_name, str(e)))
    
    print(f"\\n結果: {success_count}/{len(modules_to_test)} モジュールのインポートに成功")
    
    if failed_imports:
        print("\\n失敗したモジュール:")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    
    return True

def test_pyside6():
    \"\"\"PySide6の基本動作をテスト\"\"\"
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        
        # QApplicationを作成（ただし表示はしない）
        app = QApplication([])
        
        # 基本動作テスト用のタイマー
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(100)  # 100ms後に終了
        
        print("✓ PySide6 基本動作テスト成功")
        return True
        
    except Exception as e:
        print(f"✗ PySide6 テストエラー: {e}")
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("成績入力システム - ビルド前動作テスト")
    print("=" * 60)
    
    # インポートテスト
    print("\\n1. モジュールインポートテスト")
    import_success = test_imports()
    
    # PySide6テスト  
    print("\\n2. PySide6動作テスト")
    pyside_success = test_pyside6()
    
    # 結果サマリー
    print("\\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"モジュールインポート: {'成功' if import_success else '失敗'}")
    print(f"PySide6動作: {'成功' if pyside_success else '失敗'}")
    
    if import_success and pyside_success:
        print("\\n✅ すべてのテストが成功しました！")
        print("PyInstallerでのビルドを実行できます。")
        return 0
    else:
        print("\\n❌ 一部のテストが失敗しました。")
        print("エラーを修正してからビルドを実行してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""
    
    with open("test_before_build.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("test_before_build.py を作成しました")

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("クロスプラットフォーム問題修正スクリプト")
    print("=" * 60)
    
    # 現在のディレクトリを確認
    current_dir = Path.cwd()
    print(f"現在のディレクトリ: {current_dir}")
    
    if not (current_dir / "main.py").exists():
        print("エラー: main.pyが見つかりません。プロジェクトディレクトリで実行してください。")
        return 1
    
    # 各種修正を実行
    print("\\n1. main.pyの修正")
    fix_main_py()
    
    print("\\n2. エンコーディングチェック")
    check_encoding_issues()
    
    print("\\n3. インポートチェック")
    check_import_issues()
    
    print("\\n4. テストスクリプト作成")
    create_test_script()
    
    print("\\n" + "=" * 60)
    print("修正完了！")
    print("=" * 60)
    print("次の手順:")
    print("1. python test_before_build.py でビルド前テストを実行")
    print("2. テストが成功したらWindows環境でビルドを実行")
    print("3. Windows環境では build_windows.bat を使用")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())