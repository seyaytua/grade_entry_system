# 成績入力システム

スキャンされた資料を参照しながら、効率的に学生の成績を入力・管理するデスクトップアプリケーション

## 機能

- **成績入力**: 画像プレビューを見ながら効率的に成績を入力
- **講座管理**: 講座の追加・編集・削除、CSV入出力
- **生徒名簿管理**: 生徒情報の管理、CSV入出力
- **成績一覧表**: フィルタリング・ソート機能、CSV入出力

## システム要件

- Python 3.10以上
- macOS, Windows, Linux

## インストール

```bash
# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

## Windows用配布ファイル作成

**重要: Windows用実行ファイルはWindows環境で作成する必要があります**

### Windows環境での手順

1. **環境準備**:
```cmd
# プロジェクトフォルダで実行
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

2. **ビルド実行**:
```cmd
# 自動ビルドスクリプトを使用（推奨）
build_windows.bat

# または手動実行
python build_windows.py
```

3. **配布**: 
`dist\GradeEntrySystem\` フォルダ全体を配布

### トラブルシューティング

詳細な手順とトラブルシューティングは `WINDOWS_BUILD_GUIDE.md` を参照してください。

## 🚀 GitHub Actions による自動化

このプロジェクトは GitHub Actions を使用して以下の自動化を行います：

### 自動実行されるワークフロー

- **プルリクエスト時**: コード品質チェック & Windows ビルドテスト
- **main ブランチプッシュ時**: Windows 配布ファイル自動作成
- **タグプッシュ時**: 自動リリース作成
- **毎週月曜日**: 定期メンテナンス & 依存関係チェック

### 手動実行可能なアクション

#### リリース作成
```bash
# GitHubのActionsタブから「手動リリース作成」を実行
# または、タグをプッシュして自動リリース
git tag v1.0.0
git push origin v1.0.0
```

#### 設定されたワークフロー
- `build-and-release.yml` - メインの自動ビルド & リリース
- `pr-test.yml` - プルリクエスト時のテスト
- `scheduled-maintenance.yml` - 定期メンテナンス
- `manual-release.yml` - 手動リリース作成
