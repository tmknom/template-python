# Include: minimum
-include .makefiles/minimum/Makefile
.makefiles/minimum/Makefile:
	@git clone https://github.com/tmknom/makefiles.git .makefiles >/dev/null 2>&1

# ==============================================================================
# Pythonローカル開発
# ==============================================================================

.PHONY: all
all: sync fmt lint typecheck vulture paladin coverage ## 一括実行

.PHONY: sync-online
sync-online:
	uv sync

.PHONY: sync
sync:
	uv sync --frozen --offline

.PHONY: upgrade
upgrade: ## 依存パッケージを最新版に更新（uv.lockを更新）
	uv sync --upgrade --exclude-newer "1 week"

.PHONY: security
security: lock-check no-build-check audit ## サプライチェーンセキュリティ検証

.PHONY: lock-check
lock-check: ## uv.lockとpyproject.tomlの同期を確認
	uv lock --check

.PHONY: no-build-check
no-build-check: ## 第三者依存がすべてwheelから解決できることを検証
	uv sync --no-build --no-install-project --dry-run

.PHONY: test
test: ## テスト実行
	uv run pytest

.PHONY: test-unit
test-unit: ## ユニットテスト実行
	uv run pytest tests/unit/

.PHONY: test-integration
test-integration: ## インテグレーションテスト実行
	uv run pytest tests/integration/

.PHONY: coverage
coverage: ## カバレッジの取得
	uv run pytest --cov-fail-under=100 --cov=src --cov-report=html --cov-report=term --cov-report=term-missing

.PHONY: fmt
fmt: sync ## Ruffによるコードフォーマット
	uv run ruff format . --config=pyproject.toml

.PHONY: lint
lint: ## Ruffによる静的解析
	uv run ruff check . --fix --config=pyproject.toml

.PHONY: typecheck
typecheck: ## Pyrightによる型チェック
	uv run pyright --warnings

.PHONY: audit
audit: ## 既知の脆弱性をスキャン（pip-audit）
	uv tool run pip-audit

# Vulture の confidence は 60（デフォルト）/90/100 の3段階のみ
# 60% はフレームワーク規約（Typer/Pydantic/pytest）による誤検出が多いため除外
.PHONY: vulture
vulture: ## Vultureによるデッドコード検出
	uv run vulture src/ tests/ --min-confidence 61


.PHONY: paladin
paladin: ## Paladinによる静的解析
	uv run paladin check

.PHONY: clean
clean: ## 中間ファイルを削除
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

# ==============================================================================
# リリース
# ==============================================================================

.PHONY: release
release: release/run ## Start release process
