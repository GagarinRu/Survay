#!/usr/bin/env bash
set -e

# === Функция: ожидание доступности PostgreSQL ===
wait_for_postgres() {
    echo "Ожидание готовности базы данных PostgreSQL..."
    python << END
import time
import asyncpg
import asyncio
import os

dsn = os.environ.get("POSTGRES_DSN")
if not dsn:
    raise RuntimeError("POSTGRES_DSN не задан")

async def wait_for_db():
    while True:
        try:
            conn = await asyncpg.connect(dsn)
            await conn.close()
            print("PostgreSQL доступна.")
            break
        except Exception as e:
            print(f"PostgreSQL недоступна: {e}. Жду...")
            time.sleep(2)

asyncio.run(wait_for_db())
END
}

# === Определяем тип сервиса по переменной окружения ===
SERVICE_TYPE=${SERVICE_TYPE:-app}

case "$SERVICE_TYPE" in
  app|migration)
    wait_for_postgres
    ;;
  *)
    echo "Неизвестный тип сервиса: $SERVICE_TYPE" >&2
    exit 1
    ;;
esac

# === Выполняем действия в зависимости от типа сервиса ===
case "$SERVICE_TYPE" in
  app)
    echo "Загрузка collectstatic"
    python3 manage.py collectstatic --noinput

    echo "Применение миграций"
    python3 manage.py migrate --noinput

    echo "Старт Gunicorn"
    exec gunicorn config.wsgi:application \
        --bind "${APP_GUVICORN_HOST}:${APP_GUVICORN_PORT}" \
        --workers 3 \
        --timeout 120 \
        --preload
    ;;
  migration)
    echo "Создание миграций..."
    python3 manage.py makemigrations --noinput
    echo "Выполнение миграций"
    python3 manage.py migrate --noinput
    echo "Миграции выполнены успешно"
    ;;
esac