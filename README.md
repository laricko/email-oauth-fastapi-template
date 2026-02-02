# email-oauth-fastapi-template

**Кратко:** шаблон бекенда для работы с OAuth-провайдерами (в проекте реализована Google), извлечения писем и хранения их в базе данных. Назначение — быстрый старт для сервисов, которые хотят получать доступ к почтовым ящикам пользователей через OAuth и сохранять письма для дальнейшей обработки.

---

## Технологии

- Python (>=3.13)
- FastAPI — веб-фреймворк
- SQLAlchemy (asyncio) — ORM
- Alembic — миграции БД
- PostgreSQL (через asyncpg)
- Redis — временное хранение state при OAuth и вспомогательные данные
- httpx — HTTP-клиент для вызова API провайдеров (Google)
- PyJWT — генерация JWT-токенов
- pydantic-settings — конфигурация через env

---

## Структура проекта (основные папки / файлы)

- `src/main.py` — точка входа FastAPI, регистрация роутеров
- `src/api/` — HTTP-роуты
  - `auth.py` — маршруты для OAuth-flow и получения access token
  - `emails.py` — маршруты для синхронизации и получения писем
- `src/services/` — бизнес-логика
  - `auth/` — логика OAuth, CRUD и выдача токенов
    - `providers/google.py` — реализация Google OAuth
    - `callback.py` — обработка callback и создание пользователя
    - `tokens.py` — выдача access token (JWT)
  - `emails/` — логика получения писем и их сохранения
    - `providers/google.py` — чтение писем через Gmail API
- `src/db/` — модели и утилиты для БД (SQLAlchemy)
- `src/config.py` — конфигурация через переменные окружения (`.env`)
- `src/depends.py` — зависимости FastAPI (DI), фабрики сервисов
- `docker-compose.yml` — сервисы Postgres и Redis для локальной разработки
- `Makefile` — команды: запуск dev-сервера, миграции, подключение к контейнерам
- `pyproject.toml` — зависимости проекта

---

## Флоу пользователя (пошагово)

1. Клиент запрашивает URL авторизации:
   - GET `/auth/google/start` → возвращает URL Google OAuth (включает `state`).
2. Пользователь проходит авторизацию в Google и Google вызывает callback:
   - GET `/auth/google/callback?code=...&state=...`
   - Сервис: обменивает `code` на токены Google, получает информацию о пользователе (email), создаёт/обновляет запись в БД, сохраняет в Redis связь `state -> email` и делает редирект на `http://localhost:3000/your-frontend?state=<state>`.
     > Примечание: сервис делает редирект на фронтенд по адресу `http://localhost:3000/your-frontend?state=<state>` — фронтенд должен прочитать `state` и обменять его на access token, вызвав `POST /auth/token`.
3. Фронтенд получает `state` и вызывает получение access token:
   - POST `/auth/token` с JSON `{ "state": "<state>" }` → возвращает `{ "access_token": "<JWT>" }`.
   - На сервере `state` извлекается из Redis, ищется email в БД, формируется JWT.
4. Клиент использует `Authorization: Bearer <JWT>` для доступа к защищённым API:
   - GET `/emails/addresses` — возвращает список привязанных адресов пользователя.
   - POST `/emails/sync` — запрашивает синхронизацию писем для указанного email (тело: `{ "email": "...", "count": 10 }`).
   - GET `/emails?user_email=<email>` — получает письма из БД для указанного адреса.

---

## Реализация / архитектурные детали

- OAuth: отдельно реализован провайдер Google в `services.auth.providers.google` (получение URL, обмен кода на токены, получение userinfo).
- Хранение временного `state` для безопасности OAuth: Redis (`state` хранится с TTL; ключи устанавливаются в `OAuthCallbackService`).
- Пользователи и почтовые ящики сохраняются в PostgreSQL (модели в `db.models`).
- Email sync: для Google используется Gmail REST API (через `httpx`). Сохранение новых писем проводится транзакционно в БД.
- Токены доступа: выдаются JWT.

---

## Текущие ограничения и заметки

- Редирект на `http://localhost:3000/your-frontend?state=...` — фронтенд должен обработать `state` и выполнить запрос к `/auth/token`.
- Нет тестов и CI. Нет Dockerfile для приложения (есть `docker-compose` для сервисов БД).
- Поддерживаются только Google OAuth и Gmail API; остальным провайдерам выделено место (enum ProviderType и registry в `callback.py`).

---

## Быстрый старт (локально)

1. Запустите сервисы для разработки:

```bash
# поднять postgres и redis
docker compose up -d
```

2. Создайте файл `.env` в корне проекта со значениями (пример):

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
SECRET_KEY=some-secret-for-jwt
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=template
POSTGRES_PASSWORD=template
POSTGRES_DB=template
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

3. Установите зависимости и выполните миграции (используйте предпочитаемый менеджер пакетов, например `pip`/`poetry`):

```bash
# миграции
make migrate
```

4. Запустите сервер в режиме разработки:

```bash
make dev
# или uvicorn main:app --app-dir src --reload
```

---

## Предложения по дальнейшему использованию и улучшениям

- Поддержка дополнительных OAuth-провайдеров (Yandex и др.) через расширение `ProviderType` и регистрацию провайдеров.
- Реализация фоновой синхронизации писем (Celery/RQ/Temporal) и/или CRON-джобы.
- Добавить пагинацию и фильтрацию для получения писем, полнотекстовый поиск.
- Добавить тесты (unit + integration), настроить CI (GitHub Actions).
- Создать `Dockerfile` для приложения и пример production-docker-compose/helm chart.
- Улучшить безопасность: ротация refresh-токенов, хранение секретов, rate limiting, логирование и мониторинг.

---

## Дополнительно

- Миграции: `make makemigrations` (создание) и `make migrate` (применение).
- Для отладки БД/Redis можно подключиться к контейнерам: `make psql`, `make redis_cli`.
