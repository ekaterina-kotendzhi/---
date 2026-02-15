"""
Драйвер для работы с PostgreSQL.
Подключение через .env (как в main.py). CRUD-методы для любых таблиц.
Использование во внешних проектах: скопируйте postgres_driver.py и добавьте
в зависимости psycopg2-binary и python-dotenv.
"""

import types
import os
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor


# Значение по умолчанию для поиска .env — рядом с этим файлом
_DEFAULT_ENV_PATH = Path(__file__).resolve().parent / ".env"


class PostgresDriver:
    """
    Драйвер к базе данных PostgreSQL с CRUD-методами.
    Параметры подключения читаются из переменных окружения (.env).
    """

    def __init__(self, env_path: Optional[Path] = None):
        """
        env_path: путь к файлу .env. Если None, используется .env в папке драйвера.
        """
        self._env_path = Path(env_path) if env_path else _DEFAULT_ENV_PATH
        self._conn = None

    def connect(self, env_path: Optional[Path] = None) -> "PostgresDriver":
        """
        Устанавливает соединение с PostgreSQL.
        Переменные: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD.
        """
        path = Path(env_path) if env_path else self._env_path
        load_dotenv(dotenv_path=path)

        self._conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "test"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            options="-c client_encoding=UTF8",
        )
        self._conn.autocommit = True
        return self

    def close(self) -> None:
        """Закрывает соединение с БД."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _ensure_connected(self) -> None:
        if not self._conn or self._conn.closed:
            self.connect()

    def _build_where(self, where: dict) -> Tuple[str, list]:
        """Формирует фрагмент WHERE и список параметров из словаря."""
        if not where:
            return "", []
        parts = [f'"{k}" = %s' for k in where]
        return " AND ".join(parts), list(where.values())

    # --- CRUD ---

    def create(self, table: str, data: dict) -> Optional[dict]:
        """
        INSERT в таблицу. data — словарь {имя_колонки: значение}.
        Возвращает вставленную строку (RETURNING *) или None при ошибке.
        """
        self._ensure_connected()
        cols = list(data.keys())
        placeholders = ", ".join("%s" for _ in cols)
        columns = ", ".join(f'"{c}"' for c in cols)
        sql = f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders}) RETURNING *'
        try:
            with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, list(data.values()))
                row = cur.fetchone()
                return dict(row) if row else None
        except Error:
            sql_no_return = f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})'
            with self._conn.cursor() as cur:
                cur.execute(sql_no_return, list(data.values()))
            return None

    def read(
        self,
        table: str,
        columns: str = "*",
        where: Optional[dict] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[dict]:
        """
        SELECT из таблицы. Возвращает список словарей (ключ — имя колонки).
        columns: строка колонок, например "id, name" или "*".
        where: словарь {колонка: значение} для условия WHERE.
        order_by: например "id DESC".
        limit: максимальное число строк.
        """
        self._ensure_connected()
        sql = f'SELECT {columns} FROM "{table}"'
        params = []
        if where:
            where_sql, params = self._build_where(where)
            sql += " WHERE " + where_sql
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)

        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or None)
            return [dict(row) for row in cur.fetchall()]

    def update(self, table: str, data: dict, where: dict) -> int:
        """
        UPDATE таблицы. data — что обновить, where — условие.
        Возвращает количество обновлённых строк.
        """
        self._ensure_connected()
        if not where:
            raise ValueError("update() требует условие where")
        set_parts = [f'"{k}" = %s' for k in data]
        set_sql = ", ".join(set_parts)
        where_sql, where_params = self._build_where(where)
        params = list(data.values()) + where_params
        sql = f'UPDATE "{table}" SET {set_sql} WHERE {where_sql}'
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.rowcount

    def delete(self, table: str, where: dict) -> int:
        """
        DELETE из таблицы по условию where.
        Возвращает количество удалённых строк.
        """
        self._ensure_connected()
        if not where:
            raise ValueError("delete() требует условие where (для безопасности)")
        where_sql, params = self._build_where(where)
        sql = f'DELETE FROM "{table}" WHERE {where_sql}'
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.rowcount

    def execute(self, sql: str, params: Optional[tuple] = None) -> List[dict]:
        """
        Выполняет произвольный SQL с параметрами (%s). Параметры передавать кортежем.
        Для SELECT возвращает список словарей. Для INSERT/UPDATE/DELETE возвращает [].
        """
        self._ensure_connected()
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            if cur.description:
                return [dict(row) for row in cur.fetchall()]
            return []

    def create_table_if_not_exists(
        self, model: Union[types.ModuleType, str]
    ) -> None:
        """
        Создаёт таблицу по DDL из модели, если она не существует.
        model: модуль в формате user.py (с константой *_TABLE_DDL или *_DDL, содержащей CREATE TABLE),
               либо строка с DDL.
        """
        self._ensure_connected()
        ddl = self._get_ddl_from_model(model)
        with self._conn.cursor() as cur:
            cur.execute(ddl)

    def _get_ddl_from_model(self, model: Union[types.ModuleType, str]) -> str:
        """Извлекает DDL из модуля модели или возвращает строку как есть."""
        if isinstance(model, str):
            return model.strip()
        for name in dir(model):
            if name.endswith("_DDL") and name.isupper():
                val = getattr(model, name)
                if isinstance(val, str) and "CREATE TABLE" in val.upper():
                    return val.strip()
        raise ValueError(
            f"В модуле {getattr(model, '__name__', model)} не найдена "
            "константа *_DDL с CREATE TABLE"
        )

    def __enter__(self) -> "PostgresDriver":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


# --- Класс для таблиц users и orders (схема public) ---

class UsersOrdersDb:
    """
    Соединение и CRUD для таблиц users и orders.
    Транзакции: with db.conn: ... (autocommit=False).
    """

    USERS_DDL = """
        CREATE TABLE IF NOT EXISTS users (
            id         SERIAL PRIMARY KEY,
            name       TEXT NOT NULL,
            age        INT CHECK (age >= 0),
            email      VARCHAR(255),
            city       VARCHAR(100),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """
    ORDERS_DDL = """
        CREATE TABLE IF NOT EXISTS orders (
            id         SERIAL PRIMARY KEY,
            user_id    INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount     NUMERIC(10,2) NOT NULL,
            status     VARCHAR(20) DEFAULT 'new',
            item_name  VARCHAR(200),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """

    def __init__(self, env_path: Optional[Path] = None):
        self._env_path = Path(env_path) if env_path else _DEFAULT_ENV_PATH
        self._conn = None

    def connect(self, env_path: Optional[Path] = None) -> "UsersOrdersDb":
        path = Path(env_path) if env_path else self._env_path
        load_dotenv(dotenv_path=path)
        self._conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "test"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            options="-c client_encoding=UTF8",
        )
        self._conn.autocommit = False  # транзакции через with conn
        return self

    @property
    def conn(self):
        """Соединение для использования в with conn: (commit/rollback)."""
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def create_tables(self) -> None:
        """Создаёт таблицы users и orders в схеме public (IF NOT EXISTS). Таблицы сохраняются в базе."""
        with self._conn.cursor() as cur:
            cur.execute(self.USERS_DDL)
            cur.execute(self.ORDERS_DDL)
        self._conn.commit()

    def truncate_tables(self) -> None:
        """Очищает таблицы (сначала orders из-за FK). Для чистого примера при каждом запуске."""
        with self._conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE orders, users RESTART IDENTITY CASCADE")
        self._conn.commit()

    def add_user(
        self,
        name: str,
        age: int,
        email: Optional[str] = None,
        city: Optional[str] = None,
    ) -> int:
        """Добавляет пользователя. Возвращает id. Вызывать внутри with db.conn:."""
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, age, email, city) VALUES (%s, %s, %s, %s) RETURNING id",
                (name, age, email, city),
            )
            row = cur.fetchone()
            return row[0] if row else 0

    def add_order(
        self,
        user_id: int,
        amount: float,
        status: str = "new",
        item_name: Optional[str] = None,
    ) -> None:
        """Добавляет заказ. Вызывать внутри with db.conn:."""
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (user_id, amount, status, item_name) VALUES (%s, %s, %s, %s)",
                (user_id, amount, status, item_name),
            )

    def get_user_totals(self) -> List[Tuple[str, float]]:
        """
        Сумма заказов по каждому пользователю (LEFT JOIN).
        Все пользователи, даже без заказов. Сортировка по сумме по убыванию.
        Возвращает список пар (name, total).
        """
        sql = """
            SELECT u.name, COALESCE(SUM(o.amount), 0) AS total
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name
            ORDER BY total DESC
        """
        with self._conn.cursor() as cur:
            cur.execute(sql)
            return [(row[0], float(row[1])) for row in cur.fetchall()]

    def delete_user(self, user_id: int) -> int:
        """Удаляет пользователя (проверка ON DELETE CASCADE). Вызывать внутри with db.conn:."""
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            return cur.rowcount
