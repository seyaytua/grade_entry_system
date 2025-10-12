#!/bin/bash

set -e  # エラーで停止

echo "🔧 ローカルビルドを開始します..."

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "❌ 仮想環境が見つかりません。venv を作成してください。"
    exit 1
fi

# 仮想環境を有効化
source venv/bin/activate

# 古いビルドをクリア
echo "🧹 古いビルドをクリア中..."
rm -rf build/ dist/

# PyInstaller のインストール
echo "📦 PyInstaller をインストール中..."
pip install --upgrade pyinstaller

# ビルド実行
echo "🔨 PyInstaller でビルド中..."
pyinstaller grade_entry_system.spec

# ビルド成功確認
if [ -d "dist/GradeEntrySystem.app" ]; then
    echo "✅ ビルド完了！"
    echo "📂 出力先: dist/GradeEntrySystem.app"
    
    # 実行可能ファイルの確認
    if [ -f "dist/GradeEntrySystem.app/Contents/MacOS/GradeEntrySystem" ]; then
        echo "✅ 実行可能ファイルが存在します"
    else
        echo "❌ 実行可能ファイルが見つかりません"
        exit 1
    fi
else
    echo "❌ ビルドに失敗しました"
    exit 1
fi
