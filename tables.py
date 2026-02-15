"""
Модель стола для бронирования в ресторане.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class RestaurantTable:
    """
    Модель стола ресторана.
    Каждый экземпляр описывает один конкретный стол.
    Соответствует таблице restaurant_tables в PostgreSQL.
    """

    id: int
    number: int
    capacity: int
    zone: Optional[str] = None
    is_window: bool = False
    created_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> "RestaurantTable":
        """
        Создаёт RestaurantTable из словаря (результат PostgresDriver.read/create).
        Игнорирует лишние ключи.
        """
        return cls(
            id=row["id"],
            number=row["number"],
            capacity=row["capacity"],
            zone=row.get("zone"),
            is_window=row.get("is_window", False),
            created_at=row.get("created_at"),
        )

    def to_dict(self, exclude_id: bool = False) -> dict[str, Any]:
        """
        Преобразует модель в словарь для INSERT/UPDATE.
        exclude_id=True — для INSERT (id генерируется БД).
        """
        data = {
            "number": self.number,
            "capacity": self.capacity,
            "zone": self.zone,
            "is_window": self.is_window,
        }
        if not exclude_id and self.id:
            data["id"] = self.id
        return {k: v for k, v in data.items() if v is not None}


# DDL для создания таблицы restaurant_tables (для миграций или инициализации)
RESTAURANT_TABLES_DDL = """
CREATE TABLE IF NOT EXISTS restaurant_tables (
    id         SERIAL PRIMARY KEY,
    number     INT NOT NULL UNIQUE,
    capacity   INT NOT NULL CHECK (capacity > 0),
    zone       VARCHAR(100),
    is_window  BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
)
"""
