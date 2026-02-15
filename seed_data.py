"""
Скрипт заполнения БД тестовыми данными.
Перед заполнением очищает таблицы — ID начинаются с 1, 2, 3...
Добавляет ≥7 пользователей, ≥7 столов, ≥5 бронирований.
Запуск: python seed_data.py
Проверка в PgAdmin: SELECT * FROM users; SELECT * FROM restaurant_tables; SELECT * FROM bookings;
"""

from datetime import date, time

import backend


def seed_users():
    """Добавляет 7+ пользователей (8 шт). ID будут 1, 2, 3, ..."""
    users = [
        ("Анна", "Иванова", "anna@mail.ru", "+7-999-111-11-11"),
        ("Борис", "Петров", "boris@mail.ru", "+7-999-222-22-22"),
        ("Виктория", "Сидорова", "victoria@mail.ru", "+7-999-333-33-33"),
        ("Григорий", "Козлов", "greg@mail.ru", "+7-999-444-44-44"),
        ("Дарья", "Морозова", "darya@mail.ru", "+7-999-555-55-55"),
        ("Егор", "Волков", "egor@mail.ru", "+7-999-666-66-66"),
        ("Зоя", "Соколова", "zoya@mail.ru", "+7-999-777-77-77"),
        ("Илья", "Лебедев", "ilya@mail.ru", "+7-999-888-88-88"),
    ]
    for name, surname, email, phone in users:
        u = backend.create_user(name=name, surname=surname, email=email, phone=phone)
        if u:
            print(f"  User: {name} {surname} (id={u.id})")
    print(f"  Итого пользователей: {len(users)}")


def seed_tables():
    """Добавляет 7+ столов. ID будут 1, 2, 3, ..."""
    tables = [
        (1, 2, "У окна", True),
        (2, 4, "Основной зал", False),
        (3, 2, "У окна", True),
        (4, 6, "Основной зал", False),
        (5, 4, "Терраса", False),
        (6, 2, "Основной зал", False),
        (7, 8, "Банкетный зал", False),
        (8, 4, "Терраса", False),
    ]
    for number, capacity, zone, is_window in tables:
        t = backend.create_table(number=number, capacity=capacity, zone=zone, is_window=is_window)
        if t:
            print(f"  Table: №{number}, {capacity} мест, {zone} (id={t.id})")
    print(f"  Итого столов: {len(tables)}")


def seed_bookings():
    """Добавляет 5+ бронирований. ID будут 1, 2, 3, ... Время не пересекается (по 2 ч на бронь)."""
    tables = backend.read_restaurant_tables()
    users_list = backend.read_users()
    if len(tables) < 5 or len(users_list) < 5:
        print("  Недостаточно пользователей или столов.")
        return
    # После truncate id пользователей и столов = 1, 2, 3...
    table_ids = [t.id for t in tables[:7]]
    user_ids = [u.id for u in users_list[:7]]
    bookings = [
        (user_ids[0], table_ids[0], date(2025, 2, 20), time(18, 0), 2, "День рождения"),
        (user_ids[1], table_ids[1], date(2025, 2, 20), time(19, 0), 4, None),
        (user_ids[2], table_ids[2], date(2025, 2, 20), time(20, 0), 2, None),
        (user_ids[3], table_ids[3], date(2025, 2, 21), time(18, 30), 6, "Корпоратив"),
        (user_ids[4], table_ids[4], date(2025, 2, 21), time(19, 0), 4, None),
        (user_ids[5], table_ids[5], date(2025, 2, 22), time(12, 0), 2, "Обед"),
        (user_ids[6], table_ids[6], date(2025, 2, 22), time(14, 0), 8, "Свадьба"),
    ]
    for user_id, table_id, bdate, btime, guests, comment in bookings:
        b = backend.create_booking(
            user_id=user_id,
            table_id=table_id,
            booking_date=bdate,
            booking_time=btime,
            guests_count=guests,
            comment=comment,
        )
        if b:
            print(f"  Booking: user={user_id}, table={table_id}, {bdate} {btime} (id={b.id})")
    print(f"  Итого бронирований: {len(bookings)}")


def main():
    print("Заполнение БД тестовыми данными...")
    backend.init_tables()
    print("Очистка таблиц (ID начнутся с 1)...")
    backend.truncate_all_tables()
    print("\nПользователи:")
    seed_users()
    print("\nСтолы:")
    seed_tables()
    print("\nБронирования:")
    seed_bookings()
    print("\n--- Проверка get_all_bookings ---")
    all_bookings = backend.get_all_bookings()
    for b in all_bookings:
        print(f"  {b.id}: user={b.user_id} table={b.table_id} {b.booking_date} {b.booking_time} guests={b.guests_count}")
    print(f"\nВсего бронирований: {len(all_bookings)}")
    print("\nГотово. Проверьте данные в PgAdmin:")
    print("  - Таблица users")
    print("  - Таблица restaurant_tables")
    print("  - Таблица bookings")


if __name__ == "__main__":
    main()
