@echo off
chcp 65001 > nul
echo ================================================================
echo          成績入力システム - Windows用配布ファイル作成
echo ================================================================
echo.

REM 現在のディレクトリを保存
set ORIGINAL_DIR=%CD%

REM プロジェクトディレクトリに移動
cd /d "%~dp0"

REM Python環境チェック
python --version > nul 2>&1
if errorlevel 1 (
    echo [エラー] Pythonがインストールされていません。
    echo Python 3.10以上をインストールしてください。
    pause
    exit /b 1
)

echo [情報] Python環境を確認中...
python --version

REM 仮想環境の確認・作成
if not exist "venv" (
    echo [情報] 仮想環境を作成中...
    python -m venv venv
    if errorlevel 1 (
        echo [エラー] 仮想環境の作成に失敗しました。
        pause
        exit /b 1
    )
)

REM 仮想環境をアクティベート
echo [情報] 仮想環境をアクティベート中...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [エラー] 仮想環境のアクティベートに失敗しました。
    pause
    exit /b 1
)

REM 依存関係をインストール
echo [情報] 依存関係をインストール中...
pip install -r requirements.txt
if errorlevel 1 (
    echo [エラー] 依存関係のインストールに失敗しました。
    pause
    exit /b 1
)

REM PyInstallerをインストール
echo [情報] PyInstallerをインストール中...
pip install pyinstaller
if errorlevel 1 (
    echo [エラー] PyInstallerのインストールに失敗しました。
    pause
    exit /b 1
)

REM 古いビルドファイルを削除
if exist "build" (
    echo [情報] 古いbuildディレクトリを削除中...
    rmdir /s /q build
)

if exist "dist" (
    echo [情報] 古いdistディレクトリを削除中...
    rmdir /s /q dist
)

REM PyInstallerでビルド実行
echo [情報] Windows用実行ファイルをビルド中...
echo これには数分かかる場合があります...
pyinstaller --clean grade_entry_system.spec
if errorlevel 1 (
    echo [エラー] ビルドに失敗しました。
    echo エラーログを確認してください。
    pause
    exit /b 1
)

REM ビルド結果を確認
if exist "dist\GradeEntrySystem\GradeEntrySystem.exe" (
    echo.
    echo ================================================================
    echo                       ビルド成功！
    echo ================================================================
    echo.
    echo [配布ファイルの場所]
    echo %CD%\dist\GradeEntrySystem\
    echo.
    echo [実行ファイル]
    echo GradeEntrySystem.exe
    echo.
    echo [配布方法]
    echo 1. distフォルダ内のGradeEntrySystemフォルダ全体をコピー
    echo 2. エンドユーザーに配布
    echo 3. GradeEntrySystem.exeを実行してアプリケーションを起動
    echo.
    echo [注意事項]
    echo - 初回実行時にWindows Defenderの警告が出る場合があります
    echo - 管理者として実行することを推奨します
    echo.
    
    REM ファイルサイズを表示
    for %%F in ("dist\GradeEntrySystem\GradeEntrySystem.exe") do (
        echo [実行ファイルサイズ] %%~zF bytes
    )
    
    echo.
    echo [テスト実行] 
    choice /m "ビルドした実行ファイルをテスト実行しますか？"
    if errorlevel 2 goto end
    echo 実行ファイルを起動中...
    start "" "dist\GradeEntrySystem\GradeEntrySystem.exe"
    
) else (
    echo.
    echo [エラー] 実行ファイルが生成されませんでした。
    echo ビルドログを確認してください。
    pause
    exit /b 1
)

:end
echo.
echo ================================================================
echo                    処理が完了しました
echo ================================================================
pause

REM 元のディレクトリに戻る
cd /d "%ORIGINAL_DIR%"