# Online School

Учебный проект онлайн-школы на Django + DRF с автоматическим деплоем
через GitHub Actions на удалённый сервер.

## Стек

- Python 3.12, Django 5.2, DRF, drf-yasg (Swagger)
- PostgreSQL 16
- Redis 7 + Celery (worker + beat), django-celery-beat
- Stripe для оплат
- Gunicorn (WSGI-сервер в проде)
- Docker + Docker Compose v2
- Nginx (реверс-прокси на сервере)
- GitHub Actions (lint + tests + build + deploy)

## Структура репозитория

```
online_school/
├── .github/workflows/ci-cd.yml    # CI/CD пайплайн
├── config/                         # настройки Django (settings, urls, celery)
├── lms/                            # приложение «курсы, уроки»
├── users/                          # приложение «пользователи, оплаты»
├── Dockerfile                      # сборка образа
├── docker-compose.yml              # dev-окружение (runserver, bind-mount)
├── docker-compose.prod.yml         # prod-окружение (gunicorn, image из Docker Hub)
├── .env.sample                     # шаблон переменных окружения
├── pyproject.toml                  # зависимости Poetry
└── README.md
```

## Локальная разработка

### Требования

- Docker Desktop 4.x или Docker Engine 24+
- Docker Compose v2 (встроен в Docker Desktop)

### Первый запуск

1. Склонируй репозиторий:

   ```bash
   git clone https://github.com/viktorefimovich/online_school.git
   cd online_school
   ```

2. Создай файл `.env` из шаблона и заполни своими значениями:

   ```bash
   cp .env.sample .env
   ```

   Минимум заполни `SECRET_KEY`, `DATABASE_USER`, `DATABASE_PASSWORD`.
   Для локальной разработки `DATABASE_HOST=db`, `REDIS_URL=redis://redis:6379/0`
   (значения из шаблона).

3. Собери и запусти все сервисы одной командой:

   ```bash
   docker compose up --build
   ```

   Первый запуск займёт несколько минут (сборка образа, скачивание Postgres
   и Redis).

4. Приложение будет доступно по адресам:

   - API: http://localhost:8000/
   - Swagger: http://localhost:8000/swagger/
   - Admin: http://localhost:8000/admin/

### Создать суперпользователя

В отдельном терминале (контейнеры должны быть запущены):

```bash
docker compose exec web python manage.py createsuperuser
```

### Запуск тестов локально

```bash
docker compose exec web python manage.py test
```

Тесты гоняются внутри контейнера, чтобы `DATABASE_HOST=db` корректно
резолвился через сеть compose.

### Линтер

```bash
poetry run flake8 .
```

Конфиг лежит в `.flake8`. Максимальная длина строки — 119 символов.

### Полезные команды для dev

```bash
# Запуск в фоне
docker compose up -d

# Логи всех сервисов
docker compose logs -f

# Логи отдельного сервиса
docker compose logs -f celery

# Остановить, не удаляя данные
docker compose stop

# Остановить и удалить контейнеры (volumes останутся, данные не пропадут)
docker compose down

# Полная очистка вместе с данными БД и Redis
docker compose down -v

# Зайти в shell контейнера web
docker compose exec web bash

# Применить миграции вручную
docker compose exec web python manage.py migrate
```

### Архитектура dev-сервисов

| Сервис | Образ | Порт наружу | Назначение |
|---|---|---|---|
| `web` | свой (Dockerfile) | 8000 | Django runserver |
| `db` | postgres:16-alpine | — (только expose) | PostgreSQL |
| `redis` | redis:7-alpine | — (только expose) | Брокер Celery |
| `celery` | свой (Dockerfile) | — | Celery worker |
| `celery-beat` | свой (Dockerfile) | — | Планировщик задач |

Данные БД хранятся в volume `pg_data`, данные Redis — в `redis_data`,
загруженные файлы — в `media_data`. При `docker compose down` данные
сохраняются, при `docker compose down -v` — удаляются.

## Продакшен — развёртывание на сервере

В проекте есть отдельный compose-файл `docker-compose.prod.yml` для
сервера. Отличия от dev:

- Веб-сервер — Gunicorn вместо `runserver` Django.
- Образ берётся из Docker Hub (`viktorefimovich/online_school:latest`).
- Нет bind-mount кода — код запечён в образ.
- При старте контейнера выполняется `collectstatic` и `migrate`.
- Порт Django публикуется **только на loopback хоста** (`127.0.0.1:8000`),
  снаружи доступ только через Nginx на порту 80.
- Статика и media монтируются в именованные volumes для Nginx.

### Первичное развёртывание на сервере

Подразумевается чистый сервер на Ubuntu 22.04 / 24.04.

1. Подключись к серверу по SSH:

   ```bash
   ssh -l <user> <server-ip>
   ```

2. Обнови систему и установи Docker (официальная инструкция Docker):

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y ca-certificates curl gnupg
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
       -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
   https://download.docker.com/linux/ubuntu \
   $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
   | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io \
       docker-buildx-plugin docker-compose-plugin
   sudo usermod -aG docker $USER
   ```

   После `usermod` выйди и зайди заново, чтобы группа применилась.

3. Установи Nginx:

   ```bash
   sudo apt install -y nginx
   ```

4. Склонируй репозиторий и создай `.env`:

   ```bash
   cd ~
   git clone https://github.com/viktorefimovich/online_school.git
   cd online_school
   cp .env.sample .env
   nano .env  # заполни production-значения
   ```

   Обязательно проставь `DEBUG=False`, `ALLOWED_HOSTS=<server-ip>,localhost`,
   надёжный `SECRET_KEY` (без знака `$` в значениях).

5. Подними контейнеры:

   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

6. Настрой Nginx как реверс-прокси. Создай
   `/etc/nginx/sites-available/online_school`:

   ```nginx
   server {
       listen 80;
       server_name <server-ip>;

       client_max_body_size 100M;

       location /static/ {
           alias /var/lib/docker/volumes/online_school_static_data/_data/;
       }

       location /media/ {
           alias /var/lib/docker/volumes/online_school_media_data/_data/;
       }

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   Активируй и перезапусти Nginx:

   ```bash
   sudo ln -s /etc/nginx/sites-available/online_school \
       /etc/nginx/sites-enabled/
   sudo rm /etc/nginx/sites-enabled/default
   sudo nginx -t && sudo systemctl reload nginx
   ```

7. Создай суперпользователя на сервере:

   ```bash
   docker compose -f docker-compose.prod.yml exec web \
       python manage.py createsuperuser
   ```

8. Открой в браузере `http://<server-ip>/admin/`.

### Полезные команды для прода

```bash
# Статус сервисов
docker compose -f docker-compose.prod.yml ps

# Логи
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f celery

# Перезапустить только web (после обновления .env)
docker compose -f docker-compose.prod.yml up -d --force-recreate web

# Прогнать миграции вручную
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Очистить старые неиспользуемые образы
docker image prune -f
```

## CI/CD — GitHub Actions

Пайплайн описан в `.github/workflows/ci-cd.yml` и состоит из 4 jobs:

| Job | Когда запускается | Что делает |
|---|---|---|
| `lint` | push в любую ветку + PR в `main`/`develop` | flake8 по всему проекту |
| `test` | то же | `manage.py test` против сервисов Postgres + Redis в Actions |
| `build-and-push` | только push в `main` | сборка Docker-образа + push в Docker Hub |
| `deploy` | только push в `main`, после `build-and-push` | SSH на сервер, `git pull`, `docker compose pull` + `up -d` |

### Секреты GitHub

В **Settings → Secrets and variables → Actions** должны быть настроены:

| Имя | Значение |
|---|---|
| `DOCKERHUB_USERNAME` | логин в Docker Hub |
| `DOCKERHUB_TOKEN` | Personal Access Token из Docker Hub (с правами Read+Write) |
| `SSH_HOST` | IP-адрес сервера |
| `SSH_USER` | имя пользователя на сервере |
| `SSH_PRIVATE_KEY` | приватный SSH-ключ для подключения (полный, с `-----BEGIN/END-----`) |

Публичная половина SSH-ключа должна быть добавлена в
`~/.ssh/authorized_keys` пользователя на сервере.

### Поток разработки

```
feature/<name>  →  PR в develop  →  merge в develop
                                          │
                                          ▼
                                  ручное тестирование на develop
                                          │
                                          ▼
                              PR develop → main → merge
                                          │
                                          ▼
                        Actions: lint + test + build + deploy
                                          │
                                          ▼
                                   обновление прода
```

- На feature-ветках и `develop` гоняется только проверка (lint + test).
- Деплой запускается строго на push в `main`.
- Каждый успешный merge в `main` тегирует образ как `:latest` и
  дополнительно по SHA коммита (`:<sha>`), чтобы можно было откатиться.

## Лицензия

Учебный проект, образовательная цель. Бессрочное использование, без
гарантий.
