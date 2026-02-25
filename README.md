# URL Shortener

Пет-проект для изучения основ бэкенда: HTTP, REST API (FastAPI), работа с БД, валидация, JWT-аутентификация и структура приложения.

---

## План разработки

### Этап 1: Основа — HTTP и один эндпоинт

- **Цель:** понять запрос–ответ, маршруты, возврат JSON.
- **Сделать:** поднять минимальное приложение на **FastAPI**, один GET-эндпоинт (например, `/health`) и возврат JSON.
- **Изучить:** что такое HTTP метод, status code, Content-Type, как фреймворк маппит URL на функцию.

### Этап 2: REST API для создания короткой ссылки

- **Цель:** проектирование API, приём тела запроса, валидация.
- **Сделать:**
  - `POST /shorten` — принимает `{"url": "https://..."}`; возвращает короткий код (например, 6–8 символов) и короткий URL.
  - Генерация короткого кода: случайная строка или base62 от счётчика.
- **Изучить:** REST, коды ответов (201, 400, 422), валидация входных данных (URL формат, длина).

### Этап 3: Хранение данных (PostgreSQL)

- **Цель:** работа с БД из кода, простая схема данных, подключение к **PostgreSQL**.
- **Сделать:**
  - Поднять PostgreSQL (локально или через `docker-compose`: сервис `postgres`, переменная `DATABASE_URL`).
  - Таблицы: ссылки — `short_code`, `original_url`, `created_at` (опционально: счётчик переходов); пользователей добавить на Этапе 5.
  - Подключение из приложения: SQLAlchemy + драйвер `asyncpg` или `psycopg2`, конфиг из env (`DATABASE_URL`).
  - При `POST /shorten` — сохранять в БД и возвращать короткий URL; проверять уникальность `short_code`.
- **Изучить:** подключение к PostgreSQL, выполнение запросов, пул соединений, миграции (опционально: Alembic).

### Этап 4: Редирект по короткой ссылке

- **Цель:** разница между «вернуть JSON» и «вернуть редирект».
- **Сделать:**
  - `GET /<short_code>` — поиск в БД, если найдено — `302 Redirect` на `original_url`, иначе `404`.
- **Изучить:** HTTP 302 vs 301, заголовок `Location`, как браузер следует редиректу.

### Этап 5: JWT — аутентификация и защита эндпоинтов

- **Цель:** stateless-аутентификация, защита API по токену.
- **Сделать:**
  - Таблица пользователей: `username`, `password_hash` (или `email` + пароль). Хешировать пароль (например, bcrypt / passlib).
  - `POST /token` — принять логин/пароль, проверить, вернуть **JWT** (access_token, тип Bearer).
  - Защитить `POST /shorten`: требовать заголовок `Authorization: Bearer <token>`, проверять JWT (подпись, срок).
  - Редирект `GET /<short_code>` оставить публичным (без JWT).
- **Изучить:** что такое JWT (header, payload, signature), где хранить секрет (env), зависимость FastAPI для извлечения и валидации токена (OAuth2PasswordBearer + ручная проверка или библиотека `python-jose`).

### Этап 6: Улучшения и практики

- **Цель:** структура проекта, конфиг, обработка ошибок.
- **Сделать:**
  - Разнести код: роуты, модель/репозиторий для ссылок, генерация кода, конфиг (база, длина кода, JWT secret).
  - Централизованная обработка ошибок (невалидный URL, не найденный код, 401 Unauthorized).
  - Опционально: лимит длины исходного URL, привязка ссылок к пользователю (user_id в таблице ссылок).
- **Изучить:** слои приложения (handlers → service → repository), конфиг через переменные окружения.

### Этап 7 (опционально): Docker и окружение

- **Цель:** запуск приложения и PostgreSQL в контейнерах.
- **Сделать:** доработать `dockerfile` и `docker-compose.yml`: сервис приложения (FastAPI) + сервис **PostgreSQL**; в приложении использовать `DATABASE_URL` от хоста БД (например, `postgresql://user:pass@db:5432/urlshortener`).
- **Изучить:** образ, порты, volumes для данных PostgreSQL, переменные окружения в Docker.

---

## Стек

- Python 3.12
- **FastAPI**
- **PostgreSQL** (SQLAlchemy + psycopg2 или asyncpg)
- **JWT** (например, `python-jose[cryptography]`), passlib + bcrypt для паролей
- Опционально: Docker, Docker Compose (приложение + Postgres)

---

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# PostgreSQL: локально или через Docker
# docker-compose up -d postgres
# Задать DATABASE_URL, например: postgresql://user:password@localhost:5432/urlshortener

# Запуск приложения — после реализации Этапа 1
# uvicorn app.main:app --reload
```

---

## API (кратко)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка работы сервиса (JSON). |
| POST | `/token` | Логин: тело `username` + `password`. Возвращает JWT (access_token). |
| POST | `/shorten` | **Требует JWT.** Тело: `{"url": "https://..."}`. Возвращает короткий код и URL. |
| GET | `/<short_code>` | Публичный редирект 302 на исходный URL или 404. |

---

## Структура проекта (рекомендуемая)

```
URL shortener/
├── README.md
├── requirements.txt
├── dockerfile
├── docker-compose.yml
├── .env.example
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routes.py
│   ├── auth.py          # JWT: создание/проверка токена, зависимость
│   ├── models.py
│   └── shortcode.py
└── tests/
```
