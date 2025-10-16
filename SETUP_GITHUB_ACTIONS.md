# GitHub Actions セットアップ手順

## ⚠️ 重要: マージ後の手動設定が必要

現在の環境制限により、GitHub Actionsワークフローファイルは直接プッシュできません。
マージ後に以下の手順で手動設定してください。

## 📋 設定手順

### 1. ワークフローディレクトリ作成

リポジトリのルートで以下のディレクトリを作成：
```
.github/
└── workflows/
```

### 2. ワークフローファイル作成

以下の4つのYAMLファイルを `.github/workflows/` ディレクトリに作成：

#### A. `build-and-release.yml`
- **目的**: メインブランチのプッシュ時に自動ビルド & リリース
- **内容**: 本PR内の `.github/workflows/build-and-release.yml` をコピー

#### B. `pr-test.yml`  
- **目的**: プルリクエスト時の自動テスト
- **内容**: 本PR内の `.github/workflows/pr-test.yml` をコピー

#### C. `scheduled-maintenance.yml`
- **目的**: 週次の定期メンテナンス
- **内容**: 本PR内の `.github/workflows/scheduled-maintenance.yml` をコピー

#### D. `manual-release.yml`
- **目的**: 手動でのリリース作成
- **内容**: 本PR内の `.github/workflows/manual-release.yml` をコピー

### 3. 設定ファイル追加

#### A. `.flake8`
```ini
[flake8]
max-line-length = 127
extend-ignore = 
    E203,  # whitespace before ':'
    E501,  # line too long (handled by black)
    W503,  # line break before binary operator
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    build,
    dist,
    .eggs,
    *.egg-info,
    .pytest_cache,
    .mypy_cache
per-file-ignores =
    __init__.py:F401  # imported but unused
```

#### B. `pyproject.toml`
```toml
[tool.black]
line-length = 127
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.eggs
  | \.git
  | \.venv
  | venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 127
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

## 🚀 動作テスト手順

### 1. プルリクエストテスト
新しいプルリクエストを作成して自動テストが実行されることを確認

### 2. ビルドテスト
mainブランチにコミットして自動ビルドが実行されることを確認

### 3. リリーステスト
```bash
git tag v0.1.0-test
git push origin v0.1.0-test
```

### 4. 手動リリーステスト
GitHub の Actions タブから「手動リリース作成」を実行

## 📊 期待される動作

### 自動実行されるアクション
- ✅ プルリクエスト作成時: 自動テスト & コメント
- ✅ mainブランチプッシュ時: Windows配布ファイル作成
- ✅ タグプッシュ時: 自動リリース作成
- ✅ 毎週月曜日: 定期メンテナンス

### 手動実行可能なアクション  
- ✅ カスタムリリース作成
- ✅ 緊急メンテナンス実行

## 🔧 トラブルシューティング

### よくある問題
1. **権限エラー**: リポジトリ設定で Actions の権限を確認
2. **ビルドエラー**: Windows 環境の依存関係を確認  
3. **認証エラー**: GITHUB_TOKEN の権限を確認

### 確認ポイント
- [ ] `.github/workflows/` ディレクトリの存在
- [ ] YAML ファイルの構文エラーなし
- [ ] リポジトリの Actions 設定が有効
- [ ] 必要な権限 (`contents: write`, `issues: write`) が付与済み

## 📝 完了後の確認事項

1. Actions タブでワークフローが認識されている
2. プルリクエストで自動テストが実行される
3. mainブランチでビルドが自動実行される
4. 手動リリース作成が利用可能

---

詳細な使用方法は `GITHUB_ACTIONS_GUIDE.md` を参照してください。