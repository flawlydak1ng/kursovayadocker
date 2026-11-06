#!/usr/bin/env bash
# ci-local.sh - локальная имитация конвейера CI (те же шаги, что в preview.yml).
# Использование: scripts/ci-local.sh <git-ref> <имя-окружения> [--ttl 4h]
set -euo pipefail

REF="${1:?укажите ветку или тег git}"
NAME="${2:?укажите имя окружения}"
shift 2
REPO="$(cd "$(dirname "$0")/.." && pwd)"
ENVCTL="$REPO/platform/bin/envctl"
TAG="$(git -C "$REPO" describe --tags --always "$REF")"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "== 1. Получение исходников ($REF, версия $TAG)"
git -C "$REPO" archive "$REF" | tar -x -C "$WORK"

echo "== 2. Юнит-тесты"
docker run --rm -v "$WORK/app/api:/srv" -w /srv python:3.12-slim \
  sh -c "pip install -q --root-user-action=ignore -r requirements.txt pytest && python -m pytest -q"

echo "== 3. Сборка образов и запуск окружения"
"$ENVCTL" create "$NAME" --src "$WORK" --tag "$TAG" "$@"

echo "== 4. Дымовая проверка"
python3 "$REPO/scripts/smoke.py" --url http://127.0.0.1 \
  --host "$NAME.${TESTENV_DOMAIN:-test.local}" --expect-version "$TAG"
