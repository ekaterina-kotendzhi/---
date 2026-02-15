"""
Модель бронирования для мини-системы бронирования ресторана.
"""

from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Any, Optional


@dataclass
class Booking:
    """
    Модель бронирования.
    Связывает пользователя и стол на определённую дату и время.
    Соответствует таблице bookings в PostgreSQL.
    """

    id: int
    user_id: int  # FK -> users.id (кто бронирует)
    table_id: int  # FK -> restaurant_tables.id (какой стол забронирован)
    booking_date: date
    booking_time: time
    guests_count: int = 1
    comment: Optional[str] = None
    status: str = "confirmed"
    created_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> "Booking":
        """
        Создаёт Booking из словаря (результат PostgresDriver.read/create).
        Игнорирует лишние ключи.
        """
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            table_id=row["table_id"],
            booking_date=_parse_date(row["booking_date"]),
            booking_time=_parse_time(row["booking_time"]),
            guests_count=row.get("guests_count", 1),
            comment=row.get("comment"),
            status=row.get("status", "confirmed"),
            created_at=row.get("created_at"),
        )

    def to_dict(self, exclude_id: bool = False) -> dict[str, Any]:
        """
        Преобразует модель в словарь для INSERT/UPDATE.
        exclude_id=True — для INSERT (id генерируется БД).
        """
        data = {
            "user_id": self.user_id,
            "table_id": self.table_id,
            "booking_date": self.booking_date,
            "booking_time": self.booking_time,
            "guests_count": self.guests_count,
            "comment": self.comment,
            "status": self.status,
        }
        if not exclude_id and self.id:
            data["id"] = self.id
        return {k: v for k, v in data.items() if v is not None}


def _parse_date(value: Any) -> date:
    """Парсит date из datetime, date или строки."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = str(value)
    return date.fromisoformat(s.split()[0] if " " in s else s)


def _parse_time(value: Any) -> time:
    """Парсит time из строки или datetime."""
    if isinstance(value, time):
        return value
    s = str(value)
    if ":" in s:
        parts = s.split(":")
        h, m = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        sec = int(parts[2]) if len(parts) > 2 else 0
        return time(h, m, sec)
    return time(0, 0)


# DDL для создания таблицы bookings (для миграций или инициализации)
BOOKINGS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS bookings (
    id            SERIAL PRIMARY KEY,
    user_id       INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    table_id      INT NOT NULL REFERENCES restaurant_tables(id) ON DELETE RESTRICT,
    booking_date  DATE NOT NULL,
    booking_time  TIME NOT NULL,
    guests_count  INT NOT NULL DEFAULT 1 CHECK (guests_count > 0),
    comment       TEXT,
    status        VARCHAR(20) DEFAULT 'confirmed',
    created_at    TIMESTAMP DEFAULT NOW()
)
"""
