# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('database/migrations', 'database/migrations'),
    ],
    hiddenimports=[
        'database',
        'database.db_manager',
        'database.repositories',
        'database.repositories.course_repository',
        'database.repositories.student_repository',
        'database.repositories.grade_repository',
        'models',
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
        'views.widgets',
        'views.widgets.image_preview_widget',
        'views.widgets.student_grade_card',
        'views.widgets.split_settings_dialog',
        'views.widgets.student_assignment_item',
        'utils',
        'utils.csv_handler',
        'utils.radio_button_helper',
        'utils.pdf_splitter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GradeEntrySystem',
)
