# Money Bot (Telegram + FastAPI + GigaChat)

Telegram-бот для личного учёта финансов с интеграцией LLM. Бот работает через webhook поверх FastAPI, хранит данные в PostgreSQL и использует GigaChat для обработки пользовательского ввода.

Бот: [@your_best_finance_helper_bot](https://t.me/your_best_finance_helper_bot)

## Описание

Приложение позволяет:

- добавлять расходы и доходы,
- распределять операции по категориям,
- редактировать категории,
- получать отчёты по тратам и доходам (в том числе годовой отчёт)

Дополнительные особенности:

- интеграция с LLM (GigaChat) — разбирает текст, введенный пользователем, определяет категорию трат и сохраняет
- защита от дублей категорий: нечёткое сравнение названий через rapidfuzz, поэтому «Продукты» и «продукты » не превращаются в две разные категории
- пошаговые диалоги на конечных автоматах (FSM aiogram), состояния описаны в `bot/states.py`
- автоматические бэкапы базы через `pg_dump` по cron
- продакшн-деплой на VPS: Docker Compose, Nginx, HTTPS через Let's Encrypt

## Архитектура

Бот работает в режиме **webhook**, а не long polling: Telegram сам отправляет обновления на HTTPS-адрес приложения, FastAPI принимает их и передаёт в диспетчер aiogram.

```
Telegram  ──HTTPS──>  Nginx  ──>  FastAPI (/webhook)  ──>  aiogram Dispatcher
                                                                  │
                                           handlers (start, expense, income, report, ...)
                                                                  │
                                      finance (бизнес-логика)  ──>  PostgreSQL
                                                                  │
                                                       core/llm  ──>  GigaChat
```

Разделение по слоям:

- `api` — FastAPI-приложение: точка входа, webhook-эндпоинт, lifespan (установка и снятие webhook), зависимости
- `bot` — всё, что относится к Telegram: диспетчер, хендлеры, middleware, клавиатуры, состояния FSM
- `finance` — сервисный слой с бизнес-логикой учёта: хендлеры не ходят в базу напрямую
- `db` — модели SQLAlchemy и работа с сессиями
- `core` — конфигурация и клиент LLM (промпты, схемы ответов, клиент GigaChat)
- `migration` — миграции Alembic

## Структура проекта

```
app/
├── api/              # FastAPI: main, webhook, lifespan, dependencies
├── bot/
│   ├── handlers/     # start, expense, income, report, yearly_report, edit_category
│   ├── middlewares/
│   ├── dispatcher.py
│   ├── keyboards.py
│   ├── states.py     # состояния FSM
│   └── main.py
├── core/
│   ├── llm/          # client, prompts, schemas
│   └── config.py     # настройки приложения
├── db/               # модели и сессии
└── finance/          # сервисный слой
migration/            # Alembic
certs/                # сертификаты для webhook
```

## Развёртка

Перед началом использования необходимо клонировать репозиторий. Используйте команду в терминале:

```bash
git clone https://github.com/noskovde2015-byte/<НАЗВАНИЕ_РЕПОЗИТОРИЯ>.git
```

После этого перейдите в папку проекта:

```bash
cd <НАЗВАНИЕ_РЕПОЗИТОРИЯ>
```

Для развёртки приложения потребуется Docker и Docker Compose.

Что понадобится заранее:

- токен бота от [@BotFather](https://t.me/BotFather)
- ключ доступа к API GigaChat
- публичный домен с HTTPS — Telegram принимает webhook только по HTTPS

После этого необходимо выполнить следующие шаги:

1. Создать файл `.env` в корне проекта (переменные перечислены ниже)
2. Собрать и запустить контейнеры:

```bash
docker compose up -d --build
```

3. Применить миграции:

```bash
docker compose exec app alembic upgrade head
```

После этого приложение готово к работе и слушает порт `8002`. Webhook регистрируется при старте приложения, затем можно писать боту в Telegram.

### Переменные окружения

Пример файла `.env`:

```env
# База данных
APP_CONFIG__DB__URL=ваше подключение
POSTGRES_DB=moneybot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me

# Telegram
APP_CONFIG__BOT__TOKEN=your_bot_token
APP_CONFIG__WEBHOOK__URL=https://your-domain.com/webhook

# GigaChat
GIGACHAT_CREDENTIALS=your_credentials
APP_CONFIG__GIGACHAT__SCOPE=your_scope
```


### Состав Docker Compose

| Сервис | Описание |
|--------|----------|
| `app` | FastAPI + бот, порт `8002` |
| `db`  | PostgreSQL 18, данные хранятся в volume `postgres_data` |

## Технологии

Проект написан с использованием:

- **Python** — основной язык
- **FastAPI** — приём webhook и HTTP-слой
- **aiogram 3.x** — фреймворк для Telegram-ботов (хендлеры, FSM, middleware)
- **SQLAlchemy (async) + asyncpg** — асинхронная работа с PostgreSQL
- **PostgreSQL** — основная база данных
- **Alembic** — миграции схемы
- **GigaChat SDK** — LLM-интеграция
- **rapidfuzz** — нечёткое сравнение строк для защиты от дублей категорий
- **Pydantic** — настройки и схемы данных
- **Docker & Docker Compose** — контейнеризация
- **Nginx + Let's Encrypt** — обратный прокси и HTTPS на сервере

## Возможности бота

| Раздел | Описание |
|--------|----------|
| `start` | Приветствие и главное меню |
| Расходы | Добавление расхода с выбором категории |
| Доходы | Добавление дохода |
| Отчёты | Сводка за период |
| Годовой отчёт | Агрегированная статистика за год |
| Категории | Редактирование и управление категориями |

## Бэкапы и безопасность

- Бэкапы базы делаются через `pg_dump` по расписанию cron
- Порт PostgreSQL не публикуется наружу: в `docker-compose.yml` у сервиса `db` нет секции `ports`, база доступна только внутри сети Compose
- Секреты хранятся в `.env`, который не попадает в репозиторий (добавлен в `.gitignore`)

