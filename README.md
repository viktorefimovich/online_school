# Online School

Учебный проект онлайн-школы на Django + DRF.

## Стек

- Python 3.12, Django 5.2, DRF
- PostgreSQL 16
- Redis 7 + Celery (worker + beat)
- Stripe для оплат
- Docker + Docker Compose

## Запуск через Docker

### Требования

- Docker Desktop 4.x или Docker Engine 24+
- Docker Compose v2 (входит в Docker Desktop)

### Первый запуск

1. Склонируй репозиторий:
```bash
   git clone 
   cd online_school
```

2. Создай файл `.env` из шаблона и заполни своими значениями:
```bash
   cp .env.sample .env
```
   Минимум — заполни `SECRET_KEY`, `DATABASE_USER`, `DATABASE_PASSWORD`.

3. Собери и запусти все сервисы одной командой:
```bash
   docker compose up --build
```
   Первый запуск — несколько минут (сборка образа, загрузка Postgres и Redis).

4. Приложение будет доступно по адресу:
   - API: http://localhost:8000/
   - Swagger: http://localhost:8000/swagger/
   - Admin: http://localhost:8000/admin/

### Создать суперпользователя

В отдельном терминале (когда контейнеры запущены):

```bash
docker compose exec web python manage.py createsuperuser
```

### Полезные команды

```bash
# Запуск в фоне
docker compose up -d

# Логи всех сервисов
docker compose logs -f

# Логи только Celery
docker compose logs -f celery

# Остановить, не удаляя данные
docker compose stop

# Остановить и удалить контейнеры (volumes останутся — данные не пропадут)
docker compose down

# Полная очистка вместе с данными БД и Redis (ОСТОРОЖНО)
docker compose down -v

# Зайти в shell контейнера web
docker compose exec web bash

# Применить миграции вручную
docker compose exec web python manage.py migrate

# Собрать статику
docker compose exec web python manage.py collectstatic --noinput
```

### Архитектура сервисов

| Сервис | Образ | Порт наружу | Назначение |
|---|---|---|---|
| `web` | свой (Dockerfile) | 8000 | Django + DRF |
| `db` | postgres:16-alpine | — (только expose) | PostgreSQL |
| `redis` | redis:7-alpine | — (только expose) | Брокер Celery |
| `celery` | свой (Dockerfile) | — | Celery worker |
| `celery-beat` | свой (Dockerfile) | — | Планировщик задач |

Данные БД хранятся в volume `pg_data`, данные Redis — в `redis_data`,
загруженные файлы — в `media_data`. При `docker compose down` данные сохраняются.