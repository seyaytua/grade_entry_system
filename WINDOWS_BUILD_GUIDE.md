# Windows用配布ファイル作成ガイド

## 🎯 概要

このガイドでは、成績入力システムをWindows用の実行ファイル（.exe）として配布するための手順を説明します。

## ⚠️ 重要な注意事項

**Windows用の実行ファイルは、Windows環境でビルドする必要があります。**
- Linux環境でビルドした実行ファイルはWindowsでは動作しません
- クロスコンパイルは技術的に複雑で、PySide6などのGUIライブラリでは問題が多く発生します

## 🖥️ Windows環境でのビルド手順

### 1. 環境準備

```powershell
# Python 3.10以上がインストールされていることを確認
python --version

# プロジェクトディレクトリに移動
cd path\to\GradeEntrySystem

# 仮想環境を作成
python -m venv venv
venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
pip install pyinstaller
```

### 2. ビルド実行

```powershell
# Windows用ビルドスクリプトを実行
python build_windows.py

# または、直接PyInstallerを実行
pyinstaller --clean grade_entry_system.spec
```

### 3. 配布ファイルの確認

ビルド成功後、`dist\GradeEntrySystem\` フォルダに以下のファイルが生成されます：

```
dist/
└── GradeEntrySystem/
    ├── GradeEntrySystem.exe          # メイン実行ファイル
    ├── _internal/                    # 内部ライブラリとリソース
    │   ├── resources/               # アプリケーションリソース
    │   ├── config/                  # 設定ファイル
    │   └── ...                      # Python・PySide6ライブラリ
    └── grade_entry_system.log       # ログファイル（起動後作成）
```

## 📦 配布方法

### オプション1: フォルダ配布（推奨）
1. `dist\GradeEntrySystem` フォルダ全体をZIPで圧縮
2. エンドユーザーに配布
3. ユーザーは解凍後、`GradeEntrySystem.exe` を実行

### オプション2: インストーラー作成（上級）
Inno Setup や NSIS を使用してインストーラーを作成できます。

## 🚀 実行方法

### 管理者として実行（推奨）
Windows 10/11では、以下の手順で実行してください：

1. `GradeEntrySystem.exe`を右クリック
2. 「管理者として実行」を選択
3. Windows Defenderの警告が表示される場合は「詳細情報」→「実行」

### 通常実行
ダブルクリックで実行可能ですが、一部の機能で制限がある場合があります。

## 🛡️ セキュリティ警告への対応

### Windows Defender警告
初回実行時にWindows Defenderが警告を表示する場合があります：

**対処方法:**
1. 「詳細情報」をクリック
2. 「実行」ボタンをクリック
3. またはファイルを例外に追加

**原因:**
- デジタル署名されていない実行ファイルのため
- PyInstallerで作成された実行ファイルは一般的にこの警告が表示されます

## 🔧 トラブルシューティング

### よくある問題と解決策

#### 問題1: "MSVCP140.dll が見つかりません"
**解決策:**
Microsoft Visual C++ 再頒布可能パッケージをインストール
- [Microsoft公式ダウンロード](https://docs.microsoft.com/ja-jp/cpp/windows/latest-supported-vc-redist)

#### 問題2: "アプリケーションが起動しません"
**解決策:**
1. コマンドプロンプトから実行してエラーメッセージを確認
```cmd
cd path\to\GradeEntrySystem
GradeEntrySystem.exe
```
2. ログファイル `grade_entry_system.log` を確認

#### 問題3: "フォントが正しく表示されない"
**解決策:**
日本語フォントがインストールされていることを確認

## 📝 ビルド設定のカスタマイズ

### アイコンファイルの変更
`grade_entry_system.spec` ファイルで以下を修正：
```python
icon_path = 'resources/icons/custom_icon.ico'
```

### 起動時のコンソール表示
デバッグ用にコンソールを表示する場合：
```python
console=True,  # Falseをトゥルーに変更
```

## 🎯 配布時のチェックリスト

- [ ] Windows環境でビルド実行
- [ ] 生成された.exeファイルが正常に起動する
- [ ] 必要なリソースファイルが含まれている
- [ ] 日本語表示が正しく動作する
- [ ] データベースの読み書きが正常に動作する
- [ ] CSVファイルの入出力が正常に動作する

## 💡 最適化のヒント

### ファイルサイズの削減
不要なライブラリを除外：
```python
excludes=[
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'jupyter',
    # 使用していない場合のみ追加
],
```

### 起動速度の向上
UPX圧縮を無効化：
```python
upx=False,  # 圧縮を無効化して起動を高速化
```

---

## 🆘 サポート

問題が発生した場合は、以下の情報と共にお問い合わせください：
- Windows バージョン
- Python バージョン
- エラーメッセージの詳細
- `grade_entry_system.log` ファイルの内容