"""
Backend для системы бронирования ресторана.
CRUD-операции для Users, RestaurantTables, Bookings.
"""

from datetime import date, datetime, time, timedelta
from typing import Any, List, Optional

from postgres_driver import PostgresDriver
from models.user import User
from models.tables import RestaurantTable
from models.booking import Booking
import models.user
import models.tables
import models.booking

_driver: Optional[PostgresDriver] = None


def get_driver() -> PostgresDriver:
    """Возвращает подключённый драйвер. Создаёт таблицы при первом вызове."""
    global _driver
    if _driver is None:
        _driver = PostgresDriver().connect()
        _driver.create_table_if_not_exists(models.user)
        _driver.create_table_if_not_exists(models.tables)
        _driver.create_table_if_not_exists(models.booking)
    return _driver


# --- Users CRUD ---

def create_user(
    name: str,
    surname: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    city: Optional[str] = None,
) -> Optional[User]:
    """Создаёт пользователя."""
    d = get_driver()
    data = {"name": name, "surname": surname}
    if email:
        data["email"] = email
    if phone:
        data["phone"] = phone
    if city:
        data["city"] = city
    row = d.create("users", data)
    return User.from_db_row(row) if row else None


def read_users(user_id: Optional[int] = None) -> List[User]:
    """Читает пользователей. Если user_id задан — возвращает одного."""
    d = get_driver()
    where = {"id": user_id} if user_id is not None else None
    rows = d.read("users", where=where, order_by="id")
    return [User.from_db_row(r) for r in rows]


def update_user(
    user_id: int,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    city: Optional[str] = None,
) -> int:
    """Обновляет пользователя по id."""
    d = get_driver()
    data = {}
    if name is not None:
        data["name"] = name
    if surname is not None:
        data["surname"] = surname
    if email is not None:
        data["email"] = email
    if phone is not None:
        data["phone"] = phone
    if city is not None:
        data["city"] = city
    if not data:
        return 0
    return d.update("users", data, {"id": user_id})


def delete_user(user_id: int) -> int:
    """Удаляет пользователя по id."""
    return get_driver().delete("users", {"id": user_id})


# --- RestaurantTables CRUD ---

def create_restaurant_table(
    number: int,
    capacity: int,
    zone: Optional[str] = None,
    is_window: bool = False,
) -> Optional[RestaurantTable]:
    """Создаёт стол ресторана."""
    d = get_driver()
    data = {"number": number, "capacity": capacity, "is_window": is_window}
    if zone:
        data["zone"] = zone
    row = d.create("restaurant_tables", data)
    return RestaurantTable.from_db_row(row) if row else None


def create_table(
    number: int,
    capacity: int,
    zone: Optional[str] = None,
    is_window: bool = False,
) -> Optional[RestaurantTable]:
    """Алиас для create_restaurant_table."""
    return create_restaurant_table(number, capacity, zone, is_window)


def read_restaurant_tables(table_id: Optional[int] = None) -> List[RestaurantTable]:
    """Читает столы. Если table_id задан — возвращает один."""
    d = get_driver()
    where = {"id": table_id} if table_id is not None else None
    rows = d.read("restaurant_tables", where=where, order_by="number")
    return [RestaurantTable.from_db_row(r) for r in rows]


def update_restaurant_table(
    table_id: int,
    number: Optional[int] = None,
    capacity: Optional[int] = None,
    zone: Optional[str] = None,
    is_window: Optional[bool] = None,
) -> int:
    """Обновляет стол по id."""
    d = get_driver()
    data: dict[str, Any] = {}
    if number is not None:
        data["number"] = number
    if capacity is not None:
        data["capacity"] = capacity
    if zone is not None:
        data["zone"] = zone
    if is_window is not None:
        data["is_window"] = is_window
    if not data:
        return 0
    return d.update("restaurant_tables", data, {"id": table_id})


def delete_restaurant_table(table_id: int) -> int:
    """Удаляет стол по id."""
    return get_driver().delete("restaurant_tables", {"id": table_id})


# --- Bookings CRUD ---

# Длительность бронирования по умолчанию (минуты)
DEFAULT_BOOKING_DURATION_MINUTES = 120

# Статусы бронирования: (код в БД, название на экране)
# 1. Подтверждено — бронь принята и активна
# 2. Отменено — бронь отменена клиентом или рестораном
# 3. Завершено — визит состоялся
BOOKING_STATUSES = [
    ("confirmed", "Подтверждено"),
    ("cancelled", "Отменено"),
    ("completed", "Завершено"),
]


def booking_status_label(code: str) -> str:
    """Возвращает русское название статуса по коду."""
    for c, label in BOOKING_STATUSES:
        if c == code:
            return label
    return code


def booking_status_code_from_display(display: str) -> Optional[str]:
    """Из строки вида '1. Подтверждено' возвращает код 'confirmed'."""
    s = display.strip()
    for i, (code, label) in enumerate(BOOKING_STATUSES):
        if s == f"{i + 1}. {label}" or s == label:
            return code
    if s in [c for c, _ in BOOKING_STATUSES]:
        return s
    return None


def check_table_availability(
    table_id: int,
    booking_date: date,
    booking_time: time,
    duration_minutes: int = DEFAULT_BOOKING_DURATION_MINUTES,
    exclude_booking_id: Optional[int] = None,
) -> tuple[bool, str]:
    """
    Проверяет, свободен ли стол на указанные дату и время.
    Возвращает (доступно: bool, сообщение: str).
    Учитываются только подтверждённые бронирования (status='confirmed').
    """
    bookings = read_bookings()
    new_start = datetime.combine(booking_date, booking_time)
    new_end = new_start + timedelta(minutes=duration_minutes)

    for b in bookings:
        if b.table_id != table_id or b.booking_date != booking_date or b.status != "confirmed":
            continue
        if exclude_booking_id is not None and b.id == exclude_booking_id:
            continue
        start = datetime.combine(b.booking_date, b.booking_time)
        end = start + timedelta(minutes=duration_minutes)
        if new_start < end and new_end > start:
            return False, f"Время занято. Конфликт с бронированием ID={b.id} ({start.strftime('%H:%M')}–{end.strftime('%H:%M')})"
    return True, "Время свободно"


def create_booking(
    user_id: int,
    table_id: int,
    booking_date: date,
    booking_time: time,
    guests_count: int = 1,
    comment: Optional[str] = None,
    status: str = "confirmed",
) -> Optional[Booking]:
    """Создаёт бронирование. Проверяет наличие пользователя и стола."""
    users_found = read_users(user_id)
    if not users_found:
        raise ValueError(f"Пользователь с ID {user_id} не найден. Укажите существующий ID из вкладки «Пользователи».")
    tables_found = read_restaurant_tables(table_id)
    if not tables_found:
        raise ValueError(f"Стол с ID {table_id} не найден. Укажите существующий ID из вкладки «Столы».")
    d = get_driver()
    data = {
        "user_id": user_id,
        "table_id": table_id,
        "booking_date": booking_date,
        "booking_time": booking_time,
        "guests_count": guests_count,
        "status": status,
    }
    if comment:
        data["comment"] = comment
    row = d.create("bookings", data)
    return Booking.from_db_row(row) if row else None


def read_bookings(booking_id: Optional[int] = None) -> List[Booking]:
    """Читает бронирования. Если booking_id задан — возвращает одно."""
    d = get_driver()
    where = {"id": booking_id} if booking_id is not None else None
    rows = d.read("bookings", where=where, order_by="booking_date DESC, booking_time")
    return [Booking.from_db_row(r) for r in rows]


def get_all_bookings() -> List[Booking]:
    """Возвращает все бронирования."""
    return read_bookings()


def update_booking(
    booking_id: int,
    user_id: Optional[int] = None,
    table_id: Optional[int] = None,
    booking_date: Optional[date] = None,
    booking_time: Optional[time] = None,
    guests_count: Optional[int] = None,
    comment: Optional[str] = None,
    status: Optional[str] = None,
) -> int:
    """Обновляет бронирование по id."""
    d = get_driver()
    data: dict[str, Any] = {}
    if user_id is not None:
        data["user_id"] = user_id
    if table_id is not None:
        data["table_id"] = table_id
    if booking_date is not None:
        data["booking_date"] = booking_date
    if booking_time is not None:
        data["booking_time"] = booking_time
    if guests_count is not None:
        data["guests_count"] = guests_count
    if comment is not None:
        data["comment"] = comment
    if status is not None:
        data["status"] = status
    if not data:
        return 0
    return d.update("bookings", data, {"id": booking_id})


def delete_booking(booking_id: int) -> int:
    """Удаляет бронирование по id."""
    return get_driver().delete("bookings", {"id": booking_id})


def init_tables() -> None:
    """Инициализация: подключение и создание таблиц."""
    get_driver()


def truncate_all_tables() -> None:
    """Очищает таблицы и сбрасывает счётчики ID (начинаются с 1). Порядок: bookings → restaurant_tables → users."""
    d = get_driver()
    d.execute("TRUNCATE TABLE bookings RESTART IDENTITY CASCADE")
    d.execute("TRUNCATE TABLE restaurant_tables RESTART IDENTITY CASCADE")
    d.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")


if __name__ == "__main__":
    init_tables()
    print("Backend: таблицы созданы.")
