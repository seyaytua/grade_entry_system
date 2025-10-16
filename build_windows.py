#!/usr/bin/env python3
"""
Windows用配布ファイル作成スクリプト
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Windows用ビルドを実行"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("=" * 60)
    print("Windows用配布ファイル作成を開始")
    print("=" * 60)
    
    # 古いビルドファイルを削除
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    if build_dir.exists():
        print("古いbuildディレクトリを削除中...")
        shutil.rmtree(build_dir)
    
    if dist_dir.exists():
        print("古いdistディレクトリを削除中...")
        shutil.rmtree(dist_dir)
    
    # PyInstallerでビルド実行
    print("PyInstallerでビルド実行中...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "grade_entry_system.spec"
        ], check=True, capture_output=True, text=True)
        
        print("ビルド成功！")
        print(f"配布ファイルは以下に作成されました: {dist_dir / 'GradeEntrySystem'}")
        
        # ビルド後の構造を表示
        if dist_dir.exists():
            print("\n配布ディレクトリの内容:")
            for item in dist_dir.rglob("*"):
                if item.is_file():
                    size = item.stat().st_size
                    print(f"  {item.relative_to(dist_dir)} ({size:,} bytes)")
        
    except subprocess.CalledProcessError as e:
        print(f"ビルドエラー: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return 1
    
    print("\n=" * 60)
    print("Windows用配布ファイル作成完了")
    print("=" * 60)
    
    # Windows用の追加説明
    print("\nWindows配布時の注意事項:")
    print("1. dist/GradeEntrySystemフォルダ全体をコピーしてください")
    print("2. GradeEntrySystem.exeを実行してアプリケーションを起動します")
    print("3. 初回起動時にWindows Defenderの警告が出る場合があります")
    print("4. 必要に応じてプログラムの実行を許可してください")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())