# Система бронирования ресторана

Мини-система бронирования столов в ресторане: бэкенд на Python, PostgreSQL, графический интерфейс на tkinter.

## Возможности

- **Пользователи** — CRUD (создание, просмотр, обновление, удаление)
- **Столы** — CRUD (номер, вместимость, зона, у окна)
- **Бронирования** — CRUD, привязка к пользователю и столу
- **Проверка доступности** — перед созданием брони проверяется, не пересекается ли время с существующими (длительность брони 2 часа)

## Требования

- Python 3.10+
- PostgreSQL
- Переменные окружения в `.env` (см. ниже)

## Установка

1. Клонируйте или скопируйте проект.
2. Создайте виртуальное окружение и установите зависимости:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта:

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=booking
POSTGRES_USER=postgres
POSTGRES_PASSWORD=ваш_пароль
```

4. Создайте базу данных в PostgreSQL (например, `booking`).

## Запуск

**Графический интерфейс (основное приложение):**

```bash
python main.py
```

**Заполнение тестовыми данными (пользователи, столы, бронирования):**

```bash
python seed_data.py
```

**Только инициализация таблиц:**

```bash
python backend.py
```

## Структура проекта

| Файл / папка       | Описание |
|--------------------|----------|
| `main.py`          | GUI на tkinter (вкладки: Пользователи, Столы, Бронирования) |
| `backend.py`       | CRUD: create_user, create_table, create_booking, get_all_bookings и др. |
| `postgres_driver.py` | Драйвер PostgreSQL (подключение, CRUD, создание таблиц по DDL) |
| `models/`          | Модели: user.py, tables.py, booking.py |
| `seed_data.py`     | Скрипт заполнения БД тестовыми данными |
| `.env`             | Параметры подключения к БД (не коммитить в репозиторий) |
| `requirements.txt` | Зависимости (psycopg2-binary, python-dotenv) |

## Проверка данных в PgAdmin

1. Подключитесь к серверу PostgreSQL и базе из `.env`.
2. В схеме **public** откройте таблицы: **users**, **restaurant_tables**, **bookings**.
3. Правый клик по таблице → View/Edit Data → All Rows.

Или выполните в Query Tool:

```sql
SELECT * FROM users;
SELECT * FROM restaurant_tables;
SELECT * FROM bookings;
```

## Лицензия

Учебный проект.
