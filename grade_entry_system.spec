# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

block_cipher = None

# プロジェクトルートパスを取得（PyInstaller実行時の現在のディレクトリ）
project_root = Path(os.getcwd())

# アイコンファイルのパス（Windows用ビルド時に必要）
icon_path = project_root / 'resources' / 'icons' / 'app_icon.ico'
if not icon_path.exists():
    icon_path = None
else:
    icon_path = str(icon_path)

# データファイルとリソースの設定
datas = [
    (str(project_root / 'resources'), 'resources'),
]

# migrationsディレクトリが存在する場合のみ追加
migrations_path = project_root / 'database' / 'migrations'
if migrations_path.exists():
    datas.append((str(migrations_path), 'database/migrations'))

# コンフィグディレクトリも追加
config_path = project_root / 'config'
if config_path.exists():
    datas.append((str(config_path), 'config'))

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # 基本モジュール
        'database',
        'database.db_manager',
        'database.repositories',
        'database.repositories.course_repository',
        'database.repositories.student_repository',
        'database.repositories.grade_repository',
        
        # モデル
        'models',
        'models.course',
        'models.student',
        'models.grade',
        'models.split',
        
        # ビュー
        'views',
        'views.main_window',
        'views.grade_entry_view',
        'views.course_management_view',
        'views.student_management_view',
        'views.grade_list_view',
        'views.pdf_split_view',
        'views.widgets',
        'views.widgets.image_preview_widget',
        'views.widgets.student_grade_card',
        'views.widgets.split_settings_dialog',
        'views.widgets.student_assignment_item',
        
        # ユーティリティ
        'utils',
        'utils.csv_handler',
        'utils.radio_button_helper',
        'utils.pdf_splitter',
        
        # 設定
        'config',
        'config.settings',
        
        # PySide6の追加コンポーネント
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        
        # PIL/Pillow
        'PIL._tkinter_finder',
        
        # システムモジュール
        'sqlite3',
        'logging',
        'pathlib',
        'csv',
        'json',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GradeEntrySystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowsでコンソールウィンドウを非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
    version=None,  # バージョン情報ファイル（必要に応じて追加）
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[
        # UPX圧縮から除外するファイル
        '*.dll',
        '*.so',
        '*.dylib',
    ],
    name='GradeEntrySystem',
)
