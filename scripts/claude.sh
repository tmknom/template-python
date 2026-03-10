#!/usr/bin/env bash
set -euo pipefail

# Claude Code の初期設定スクリプト
# .claude/ ディレクトリを作成し、settings.local.json を配置する

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "${REPO_ROOT}")"
SCRIPT_DIR="${REPO_ROOT}/scripts"

CLAUDE_DIR="${REPO_ROOT}/.claude"
SOURCE_JSON="${SCRIPT_DIR}/claude.json"
DEST_JSON="${CLAUDE_DIR}/settings.local.json"

# .claude/ ディレクトリ作成
mkdir -p "${CLAUDE_DIR}"

# settings.local.json をコピー（既存ファイルは上書きしない）
if [[ -f "${DEST_JSON}" ]]; then
  echo "Already exists: ${DEST_JSON}"
  exit 0
fi

cp "${SOURCE_JSON}" "${DEST_JSON}"

# TODO をリポジトリ名に置換
sed -i "" "s|TODO|${REPO_NAME}|g" "${DEST_JSON}"

echo "Initialized: ${DEST_JSON}"
echo "Repository name: ${REPO_NAME}"
