#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成績入力システム - インポートテスト
PyInstallerビルド前の基本動作確認用
"""

import sys
import traceback
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """すべてのモジュールのインポートをテスト"""
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
    
    print(f"\n結果: {success_count}/{len(modules_to_test)} モジュールのインポートに成功")
    
    if failed_imports:
        print("\n失敗したモジュール:")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    
    return True

def test_pyside6():
    """PySide6の基本動作をテスト"""
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
    print("\n1. モジュールインポートテスト")
    import_success = test_imports()
    
    # PySide6テスト  
    print("\n2. PySide6動作テスト")
    pyside_success = test_pyside6()
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"モジュールインポート: {'成功' if import_success else '失敗'}")
    print(f"PySide6動作: {'成功' if pyside_success else '失敗'}")
    
    if import_success and pyside_success:
        print("\n✅ すべてのテストが成功しました！")
        print("PyInstallerでのビルドを実行できます。")
        return 0
    else:
        print("\n❌ 一部のテストが失敗しました。")
        print("エラーを修正してからビルドを実行してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
