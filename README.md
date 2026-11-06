# TestEnv: платформа автоматического развёртывания тестовых сред

Учебный проект к курсовой работе. Для каждой ветки или pull request автоматически создаётся
изолированное окружение (nginx + Flask + PostgreSQL) с собственным адресом `<имя>.test.local`.
Окружения удаляются вручную или автоматически по истечении срока жизни (TTL).

## Требования

- Linux-сервер (или WSL2/виртуальная машина) с Docker Engine и Docker Compose v2;
- git, curl, bash, Python 3.

## Быстрый старт

```bash
# 1. Платформенный слой: Traefik и общая сеть traefik-public
docker compose -f platform/compose.platform.yml up -d

# 2. Утилита envctl в PATH
sudo ln -s "$PWD/platform/bin/envctl" /usr/local/bin/envctl

# 3. Локальный прогон конвейера: тесты, сборка, окружение, дымовая проверка
scripts/ci-local.sh main stable --ttl 8h
scripts/ci-local.sh feature/stats pr-12 --ttl 3d

# 4. Управление окружениями
envctl list
envctl status pr-12
envctl destroy pr-12
envctl gc
```

Чтобы открыть окружение в браузере, добавьте в файл hosts строку
`127.0.0.1 stable.test.local pr-12.test.local` (или настройте DNS-запись `*.test.local`).

## Состав

| Путь | Назначение |
| --- | --- |
| `app/` | демонстрационное приложение Notes (frontend, api, db) |
| `platform/compose.platform.yml` | Traefik и сеть traefik-public |
| `platform/templates/compose.testenv.yml` | шаблон тестового окружения |
| `platform/bin/envctl` | управление окружениями (create, list, status, destroy, gc) |
| `platform/cron/envctl-gc.cron` | пример расписания очистки по TTL |
| `scripts/smoke.py` | дымовая проверка окружения |
| `scripts/ci-local.sh` | локальная имитация конвейера CI |
| `.github/workflows/` | ci.yml и preview.yml для GitHub Actions |

## Параметры envctl (переменные окружения)

| Переменная | По умолчанию | Смысл |
| --- | --- | --- |
| `TESTENV_DOMAIN` | `test.local` | базовый домен окружений |
| `TESTENV_TTL` | `4h` | срок жизни окружения по умолчанию |
| `TESTENV_MAX_ENVS` | `8` | максимальное число окружений |
| `TESTENV_ENTRY` | `http://127.0.0.1` | адрес Traefik для проверки готовности |
| `TESTENV_READY_TIMEOUT` | `120` | ожидание готовности окружения, с |
