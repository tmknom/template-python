#!/usr/bin/env bash
set -euo pipefail

# scripts/rename.sh - テンプレートパッケージリネームスクリプト
#
# 概要:
#   このリポジトリ（template-python）をベースに新しいプロジェクトを作成した後、
#   デフォルトのパッケージ名 'example' を実際のプロジェクト名に変更するスクリプト。
#
# 使い方:
#   scripts/rename.sh <new_name>
#
# 引数:
#   new_name  新しいパッケージ名
#             制約: 英小文字で始まり、英小文字・数字・アンダースコアのみ使用可能
#             例: paladin, my_app, awesome_tool
#
# 実行例:
#   scripts/rename.sh paladin
#
# 処理内容:
#   1. pyproject.toml の name / scripts / packages フィールドを更新
#   2. uv.lock の name フィールドを更新
#   3. src/example/ 配下の .py ファイルの import 文・環境変数プレフィックスを更新
#   4. tests/ 配下の .py ファイルの import 文・モジュール実行文字列・環境変数名を更新
#   5. llms.txt のパッケージパス参照を更新
#   6. README.md のパッケージパス参照を更新
#   7. docs/**/*.md のパッケージパス参照・環境変数名を更新
#   8. src/example/ ディレクトリを src/<new_name>/ にリネーム
#
# 置換除外:
#   - example.txt（docs/specs/transform/design.md 内の変換例ファイル名）
#   - .envrc.example 等の .example 拡張子ファイル
#   - .venv/、.git/、tmp/ 配下のファイル
#   - テストデータ内の値（/tmp/example のようなパス文字列）
#
# 注意:
#   実行後は 'uv sync' と 'uv run pytest' で動作確認を行うこと。

REPO_ROOT="$(git rev-parse --show-toplevel)"
OLD_NAME="example"
OLD_NAME_UPPER="EXAMPLE"

# --- 引数チェック ---
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <new_name>" >&2
    echo "  Example: $0 paladin" >&2
    exit 1
fi

NEW_NAME="$1"
NEW_NAME_UPPER="$(echo "${NEW_NAME}" | tr '[:lower:]' '[:upper:]')"

# Python パッケージ名バリデーション（英小文字始まり、英小文字・数字・アンダースコアのみ）
if [[ ! "${NEW_NAME}" =~ ^[a-z][a-z0-9_]*$ ]]; then
    echo "Error: '${NEW_NAME}' is not a valid Python package name." >&2
    echo "  Must start with a lowercase letter and contain only lowercase letters, digits, and underscores." >&2
    exit 1
fi

# 同名チェック
if [[ "${NEW_NAME}" == "${OLD_NAME}" ]]; then
    echo "Error: New name must be different from '${OLD_NAME}'." >&2
    exit 1
fi

# 既存ディレクトリチェック
if [[ -d "${REPO_ROOT}/src/${NEW_NAME}" ]]; then
    echo "Error: Directory '${REPO_ROOT}/src/${NEW_NAME}' already exists." >&2
    exit 1
fi

echo "Renaming package '${OLD_NAME}' to '${NEW_NAME}'..."
echo "  Repository: ${REPO_ROOT}"
echo ""

# =============================================================================
# Step 1: pyproject.toml
# =============================================================================
echo "[1/8] Updating pyproject.toml..."

# name = "example"
sed -i "" "s|^name = \"${OLD_NAME}\"|name = \"${NEW_NAME}\"|" "${REPO_ROOT}/pyproject.toml"

# example = "example.cli:main"  →  newname = "newname.cli:main"
sed -i "" "s|^${OLD_NAME} = \"${OLD_NAME}\.cli:main\"|${NEW_NAME} = \"${NEW_NAME}.cli:main\"|" "${REPO_ROOT}/pyproject.toml"

# packages = ["src/example"]
sed -i "" "s|packages = \[\"src/${OLD_NAME}\"\]|packages = [\"src/${NEW_NAME}\"]|" "${REPO_ROOT}/pyproject.toml"

# =============================================================================
# Step 2: uv.lock
# =============================================================================
echo "[2/8] Updating uv.lock..."
sed -i "" "s|^name = \"${OLD_NAME}\"|name = \"${NEW_NAME}\"|" "${REPO_ROOT}/uv.lock"

# =============================================================================
# Step 3: src/example/ 配下の Python ファイル
# =============================================================================
echo "[3/8] Updating src/${OLD_NAME}/ Python files..."
while IFS= read -r -d '' file; do
    sed -i "" "s|from ${OLD_NAME}\.|from ${NEW_NAME}.|g" "${file}"
    sed -i "" "s|import ${OLD_NAME}\.|import ${NEW_NAME}.|g" "${file}"
    sed -i "" "s|${OLD_NAME_UPPER}_|${NEW_NAME_UPPER}_|g" "${file}"
    sed -i "" "s|uv run ${OLD_NAME} |uv run ${NEW_NAME} |g" "${file}"
done < <(find "${REPO_ROOT}/src/${OLD_NAME}" -name "*.py" -print0)

# =============================================================================
# Step 4: tests/ 配下の Python ファイル
# =============================================================================
echo "[4/8] Updating tests/ Python files..."
while IFS= read -r -d '' file; do
    sed -i "" "s|from ${OLD_NAME}\.|from ${NEW_NAME}.|g" "${file}"
    sed -i "" "s|import ${OLD_NAME}\.|import ${NEW_NAME}.|g" "${file}"
    sed -i "" "s|\"${OLD_NAME}\.cli\"|\"${NEW_NAME}.cli\"|g" "${file}"
    sed -i "" "s|${OLD_NAME_UPPER}_|${NEW_NAME_UPPER}_|g" "${file}"
done < <(find "${REPO_ROOT}/tests" -name "*.py" -print0)

# =============================================================================
# Step 5: llms.txt
# =============================================================================
echo "[5/8] Updating llms.txt..."
sed -i "" "s|src/${OLD_NAME}/|src/${NEW_NAME}/|g" "${REPO_ROOT}/llms.txt"
sed -i "" "s|\`${OLD_NAME}\.\([a-z_][a-z0-9_.]*\)\`|\`${NEW_NAME}.\1\`|g" "${REPO_ROOT}/llms.txt"

# =============================================================================
# Step 6: README.md
# =============================================================================
echo "[6/8] Updating README.md..."
sed -i "" "s|src/${OLD_NAME}/|src/${NEW_NAME}/|g" "${REPO_ROOT}/README.md"
sed -i "" "s|\`${OLD_NAME}\.\([a-z_][a-z0-9_.]*\)\`|\`${NEW_NAME}.\1\`|g" "${REPO_ROOT}/README.md"

# =============================================================================
# Step 7: docs/**/*.md
# =============================================================================
echo "[7/8] Updating docs/ Markdown files..."

# `example.txt` の置換を防ぐプレースホルダー
PLACEHOLDER="__RENAME_PROTECTED_EXAMPLE_TXT__"

while IFS= read -r -d '' file; do
    # Step A: `example.txt` をプレースホルダーで保護
    sed -i "" "s|\`${OLD_NAME}\.txt\`|${PLACEHOLDER}|g" "${file}"

    # Step B: src/example/ 形式のパスリテラル
    sed -i "" "s|src/${OLD_NAME}/|src/${NEW_NAME}/|g" "${file}"

    # Step C: バッククォート内の `example.XXX` 形式（モジュールパス）
    # [a-z0-9_.] に : は含まれないため `example.cli:main` → `newname.cli:main` も正しく処理される
    # () が後続する場合（`example.cli.main()` など）も対応
    sed -i "" "s|\`${OLD_NAME}\.\([a-z_][a-z0-9_.]*\)()\`|\`${NEW_NAME}.\1()\`|g" "${file}"
    sed -i "" "s|\`${OLD_NAME}\.\([a-z_][a-z0-9_.]*\)\`|\`${NEW_NAME}.\1\`|g" "${file}"

    # Step C2: バッククォート内で `from example.` で始まる Python import 文
    # 例: `from example.config.path import PathConfig`
    sed -i "" "s|\`from ${OLD_NAME}\.\(.*\)\`|\`from ${NEW_NAME}.\1\`|g" "${file}"

    # Step D: バッククォートなしのモジュールパス（テーブル・コメント内の主要サブモジュール）
    sed -i "" "s|${OLD_NAME}\.\(cli\|config\|transform\|foundation\|protocol\)|${NEW_NAME}.\1|g" "${file}"

    # Step E: 環境変数プレフィックス（大文字 EXAMPLE_ および小文字 example_ の両方）
    sed -i "" "s|${OLD_NAME_UPPER}_|${NEW_NAME_UPPER}_|g" "${file}"
    sed -i "" "s|${OLD_NAME}_|${NEW_NAME}_|g" "${file}"

    # Step F: コマンド例（スペース区切り・バッククォート終端の両方）
    sed -i "" "s|uv run ${OLD_NAME} |uv run ${NEW_NAME} |g" "${file}"
    sed -i "" "s|uv run ${OLD_NAME}\`|uv run ${NEW_NAME}\`|g" "${file}"

    # Step G: バッククォート内の単体パッケージ名（`example` や `example/` の形式）
    sed -i "" "s|\`${OLD_NAME}/\`|\`${NEW_NAME}/\`|g" "${file}"
    sed -i "" "s|\`${OLD_NAME}\`|\`${NEW_NAME}\`|g" "${file}"

    # Step H: バッククォート内の packages 設定文字列（例: `packages = ["src/example"]`）
    sed -i "" "s|\"src/${OLD_NAME}\"|\"src/${NEW_NAME}\"|g" "${file}"

    # Step I: コードブロック内のディレクトリ表記（例: `└── example/`）
    sed -i "" "s|└── ${OLD_NAME}/|└── ${NEW_NAME}/|g" "${file}"

    # Step J: プレースホルダーを元に戻す
    sed -i "" "s|${PLACEHOLDER}|\`${OLD_NAME}.txt\`|g" "${file}"
done < <(find "${REPO_ROOT}/docs" -name "*.md" -print0)

# =============================================================================
# Step 8: ディレクトリリネーム（テキスト置換の後）
# =============================================================================
echo "[8/8] Renaming directory: src/${OLD_NAME}/ → src/${NEW_NAME}/..."
mv "${REPO_ROOT}/src/${OLD_NAME}" "${REPO_ROOT}/src/${NEW_NAME}"

# =============================================================================
# 完了
# =============================================================================
echo ""
echo "Done! Package '${OLD_NAME}' has been renamed to '${NEW_NAME}'."
echo ""
echo "Next steps:"
echo "  1. uv sync"
echo "  2. uv run pytest"
echo "  3. git diff --stat"
