"""
Модель пользователя для мини-системы бронирования.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class User:
    """
    Модель пользователя.
    Соответствует таблице users в PostgreSQL.
    """

    id: int
    name: str
    surname: str
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> "User":
        """
        Создаёт User из словаря (результат PostgresDriver.read/create).
        Игнорирует лишние ключи.
        """
        return cls(
            id=row["id"],
            name=row["name"],
            surname=row["surname"],
            email=row.get("email"),
            phone=row.get("phone"),
            city=row.get("city"),
            created_at=row.get("created_at"),
        )

    def to_dict(self, exclude_id: bool = False) -> dict[str, Any]:
        """
        Преобразует модель в словарь для INSERT/UPDATE.
        exclude_id=True — для INSERT (id генерируется БД).
        """
        data = {
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
        }
        if not exclude_id and self.id:
            data["id"] = self.id
        return {k: v for k, v in data.items() if v is not None}


# DDL для создания таблицы users (для миграций или инициализации)
USERS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    surname    TEXT NOT NULL,
    email      VARCHAR(255),
    phone      VARCHAR(20),
    city       VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
)
"""
