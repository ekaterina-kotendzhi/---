"""
Графический интерфейс системы бронирования ресторана.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, time
from typing import Optional

import backend


def parse_time(s: str) -> time:
    """Парсит время из строки HH:MM или HH:MM:SS."""
    parts = s.strip().split(":")
    if not parts:
        raise ValueError("Неверный формат времени")
    h = int(parts[0])
    m = int(parts[1]) if len(parts) > 1 else 0
    sec = int(parts[2]) if len(parts) > 2 else 0
    return time(h, m, sec)


def parse_date(s: str) -> date:
    """Парсит дату из строки YYYY-MM-DD."""
    return date.fromisoformat(s.strip())


class UsersTab(ttk.Frame):
    """Вкладка пользователей."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        # Create
        f_create = ttk.LabelFrame(self, text="Создать пользователя", padding=5)
        f_create.pack(fill="x", pady=5)
        ttk.Label(f_create, text="Имя:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self._create_name = ttk.Entry(f_create, width=20)
        self._create_name.grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(f_create, text="Фамилия:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self._create_surname = ttk.Entry(f_create, width=20)
        self._create_surname.grid(row=1, column=1, padx=2, pady=2)
        ttk.Label(f_create, text="Email:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self._create_email = ttk.Entry(f_create, width=20)
        self._create_email.grid(row=2, column=1, padx=2, pady=2)
        ttk.Label(f_create, text="Телефон:").grid(row=3, column=0, sticky="e", padx=2, pady=2)
        self._create_phone = ttk.Entry(f_create, width=20)
        self._create_phone.grid(row=3, column=1, padx=2, pady=2)
        ttk.Button(f_create, text="Создать", command=self._on_create).grid(row=4, column=1, pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        # Read
        f_read = ttk.LabelFrame(self, text="Список пользователей", padding=5)
        f_read.pack(fill="both", expand=True, pady=5)
        self._tree = ttk.Treeview(f_read, columns=("num", "id", "name", "surname", "email", "phone"), show="headings", height=6)
        self._tree.heading("num", text="№")
        self._tree.heading("id", text="ID")
        self._tree.heading("name", text="Имя")
        self._tree.heading("surname", text="Фамилия")
        self._tree.heading("email", text="Email")
        self._tree.heading("phone", text="Телефон")
        self._tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(f_read, orient="vertical", command=self._tree.yview)
        sb.pack(side="right", fill="y")
        self._tree.configure(yscrollcommand=sb.set)
        ttk.Button(f_read, text="Обновить", command=self._refresh).pack(pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        # Update
        f_upd = ttk.LabelFrame(self, text="Обновить пользователя", padding=5)
        f_upd.pack(fill="x", pady=5)
        ttk.Label(f_upd, text="№:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self._upd_id = ttk.Entry(f_upd, width=10)
        self._upd_id.grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(f_upd, text="Имя:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self._upd_name = ttk.Entry(f_upd, width=20)
        self._upd_name.grid(row=1, column=1, padx=2, pady=2)
        ttk.Label(f_upd, text="Фамилия:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self._upd_surname = ttk.Entry(f_upd, width=20)
        self._upd_surname.grid(row=2, column=1, padx=2, pady=2)
        ttk.Button(f_upd, text="Обновить", command=self._on_update).grid(row=3, column=1, pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        # Delete
        f_del = ttk.LabelFrame(self, text="Удалить пользователя", padding=5)
        f_del.pack(fill="x", pady=5)
        ttk.Label(f_del, text="№:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self._del_id = ttk.Entry(f_del, width=10)
        self._del_id.grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(f_del, text="Удалить", command=self._on_delete).grid(row=1, column=1, pady=5)

        self._refresh()

    def _on_create(self):
        name = self._create_name.get().strip()
        surname = self._create_surname.get().strip()
        if not name or not surname:
            messagebox.showerror("Ошибка", "Имя и фамилия обязательны")
            return
        try:
            u = backend.create_user(
                name=name,
                surname=surname,
                email=self._create_email.get().strip() or None,
                phone=self._create_phone.get().strip() or None,
            )
            if u:
                messagebox.showinfo("Успех", f"Пользователь создан (ID={u.id})")
                self._create_name.delete(0, tk.END)
                self._create_surname.delete(0, tk.END)
                self._create_email.delete(0, tk.END)
                self._create_phone.delete(0, tk.END)
                self._refresh()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать пользователя")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _refresh(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        self._users_list = backend.read_users()
        for num, u in enumerate(self._users_list, start=1):
            self._tree.insert("", tk.END, values=(num, u.id, u.name, u.surname, u.email or "", u.phone or ""))

    def _get_user_id_by_num(self, num: int) -> Optional[int]:
        """Возвращает id пользователя по № в списке."""
        if not hasattr(self, "_users_list") or not self._users_list:
            return None
        if 1 <= num <= len(self._users_list):
            return self._users_list[num - 1].id
        return None

    def _on_update(self):
        try:
            num = int(self._upd_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "№ должен быть числом")
            return
        uid = self._get_user_id_by_num(num)
        if uid is None:
            messagebox.showerror("Ошибка", f"Пользователь с № {num} не найден. Обновите список.")
            return
        name = self._upd_name.get().strip()
        surname = self._upd_surname.get().strip()
        if not name and not surname:
            messagebox.showerror("Ошибка", "Укажите имя и/или фамилию")
            return
        try:
            n = backend.update_user(uid, name=name or None, surname=surname or None)
            if n > 0:
                messagebox.showinfo("Успех", f"Обновлено записей: {n}")
                self._refresh()
            else:
                messagebox.showwarning("Внимание", "Ничего не обновлено")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_delete(self):
        try:
            num = int(self._del_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "№ должен быть числом")
            return
        uid = self._get_user_id_by_num(num)
        if uid is None:
            messagebox.showerror("Ошибка", f"Пользователь с № {num} не найден. Обновите список.")
            return
        u = next((x for x in self._users_list if x.id == uid), None)
        name = f"{u.name} {u.surname}" if u else f"№{num}"
        if not messagebox.askyesno("Подтверждение", f"Удалить пользователя {name}?"):
            return
        try:
            n = backend.delete_user(uid)
            messagebox.showinfo("Успех", f"Удалено записей: {n}")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


class TablesTab(ttk.Frame):
    """Вкладка столов."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        f_create = ttk.LabelFrame(self, text="Создать стол", padding=5)
        f_create.pack(fill="x", pady=5)
        ttk.Label(f_create, text="Номер:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self._create_number = ttk.Entry(f_create, width=10)
        self._create_number.grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(f_create, text="Вместимость:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self._create_capacity = ttk.Entry(f_create, width=10)
        self._create_capacity.grid(row=1, column=1, padx=2, pady=2)
        ttk.Label(f_create, text="Зона:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self._zone_choices = ["Терраса", "Основной зал", "У окна", "Банкетный зал", "Летняя веранда"]
        self._create_zone = ttk.Combobox(f_create, values=self._zone_choices, width=18, state="readonly")
        self._create_zone.grid(row=2, column=1, padx=2, pady=2)
        self._create_zone.set(self._zone_choices[0])
        self._create_window = tk.BooleanVar(value=False)
        ttk.Checkbutton(f_create, text="У окна", variable=self._create_window).grid(row=3, column=1, sticky="w", padx=2)
        ttk.Button(f_create, text="Создать", command=self._on_create).grid(row=4, column=1, pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        f_read = ttk.LabelFrame(self, text="Список столов", padding=5)
        f_read.pack(fill="both", expand=True, pady=5)
        self._tree = ttk.Treeview(f_read, columns=("id", "number", "capacity", "zone", "window"), show="headings", height=6)
        self._tree.heading("id", text="ID")
        self._tree.heading("number", text="Номер")
        self._tree.heading("capacity", text="Вместимость")
        self._tree.heading("zone", text="Зона")
        self._tree.heading("window", text="У окна")
        self._tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(f_read, orient="vertical", command=self._tree.yview)
        sb.pack(side="right", fill="y")
        self._tree.configure(yscrollcommand=sb.set)
        ttk.Button(f_read, text="Обновить", command=self._refresh).pack(pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        f_upd = ttk.LabelFrame(self, text="Обновить стол", padding=5)
        f_upd.pack(fill="x", pady=5)
        ttk.Label(f_upd, text="ID:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self._upd_id = ttk.Entry(f_upd, width=10)
        self._upd_id.grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(f_upd, text="Номер:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self._upd_number = ttk.Entry(f_upd, width=10)
        self._upd_number.grid(row=1, column=1, padx=2, pady=2)
        ttk.Label(f_upd, text="Вместимость:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self._upd_capacity = ttk.Entry(f_upd, width=10)
        self._upd_capacity.grid(row=2, column=1, padx=2, pady=2)
        ttk.Button(f_upd, text="Обновить", command=self._on_update).grid(row=3, column=1, pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        f_del = ttk.LabelFrame(self, text="Удалить стол", padding=5)
        f_del.pack(fill="x", pady=5)
        ttk.Label(f_del, text="ID:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self._del_id = ttk.Entry(f_del, width=10)
        self._del_id.grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(f_del, text="Удалить", command=self._on_delete).grid(row=1, column=1, pady=5)

        self._refresh()

    def _on_create(self):
        try:
            number = int(self._create_number.get())
            capacity = int(self._create_capacity.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Номер и вместимость — целые числа")
            return
        if capacity < 1:
            messagebox.showerror("Ошибка", "Вместимость должна быть >= 1")
            return
        try:
            zone_val = self._create_zone.get().strip() or None
            t = backend.create_restaurant_table(
                number=number,
                capacity=capacity,
                zone=zone_val,
                is_window=self._create_window.get(),
            )
            if t:
                messagebox.showinfo("Успех", f"Стол создан (ID={t.id})")
                self._create_number.delete(0, tk.END)
                self._create_capacity.delete(0, tk.END)
                self._create_zone.set(self._zone_choices[0])
                self._refresh()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать стол (возможно, такой номер уже есть)")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _refresh(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for t in backend.read_restaurant_tables():
            self._tree.insert("", tk.END, values=(t.id, t.number, t.capacity, t.zone or "", "Да" if t.is_window else "Нет"))

    def _on_update(self):
        try:
            tid = int(self._upd_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID должен быть числом")
            return
        number = self._upd_number.get().strip()
        capacity = self._upd_capacity.get().strip()
        try:
            num = int(number) if number else None
            cap = int(capacity) if capacity else None
        except ValueError:
            messagebox.showerror("Ошибка", "Номер и вместимость — целые числа")
            return
        if cap is not None and cap < 1:
            messagebox.showerror("Ошибка", "Вместимость должна быть >= 1")
            return
        try:
            n = backend.update_restaurant_table(tid, number=num, capacity=cap)
            if n > 0:
                messagebox.showinfo("Успех", f"Обновлено записей: {n}")
                self._refresh()
            else:
                messagebox.showwarning("Внимание", "Ничего не обновлено")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_delete(self):
        try:
            tid = int(self._del_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID должен быть числом")
            return
        if not messagebox.askyesno("Подтверждение", f"Удалить стол ID={tid}?"):
            return
        try:
            n = backend.delete_restaurant_table(tid)
            messagebox.showinfo("Успех", f"Удалено записей: {n}")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


class BookingsTab(ttk.Frame):
    """Вкладка бронирований."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        f_create = ttk.LabelFrame(self, text="Создать бронирование", padding=5)
        f_create.pack(fill="x", pady=5)
        ttk.Label(f_create, text="ID пользователя:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self._create_user_id = ttk.Entry(f_create, width=10)
        self._create_user_id.grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(f_create, text="Предпочтительный стол:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self._booking_tables_list = backend.read_restaurant_tables()
        self._create_table_display = [
            f"№{t.number} — {t.zone or '—'} ({t.capacity} мест)" for t in self._booking_tables_list
        ]
        self._create_table_combo = ttk.Combobox(
            f_create, values=self._create_table_display, width=28, state="readonly"
        )
        self._create_table_combo.grid(row=1, column=1, padx=2, pady=2)
        if self._create_table_display:
            self._create_table_combo.current(0)
        ttk.Label(f_create, text="Дата (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self._create_date = ttk.Entry(f_create, width=12)
        self._create_date.insert(0, date.today().isoformat())
        self._create_date.grid(row=2, column=1, padx=2, pady=2)
        ttk.Label(f_create, text="Время (HH:MM):").grid(row=3, column=0, sticky="e", padx=2, pady=2)
        self._create_time = ttk.Entry(f_create, width=10)
        self._create_time.insert(0, "19:00")
        self._create_time.grid(row=3, column=1, padx=2, pady=2)
        ttk.Label(f_create, text="Гостей:").grid(row=4, column=0, sticky="e", padx=2, pady=2)
        self._create_guests = ttk.Entry(f_create, width=10)
        self._create_guests.insert(0, "1")
        self._create_guests.grid(row=4, column=1, padx=2, pady=2)
        ttk.Label(f_create, text="Комментарий:").grid(row=5, column=0, sticky="e", padx=2, pady=2)
        self._create_comment = ttk.Entry(f_create, width=25)
        self._create_comment.grid(row=5, column=1, padx=2, pady=2)
        ttk.Button(f_create, text="Создать", command=self._on_create).grid(row=6, column=0, padx=2, pady=5)
        ttk.Button(f_create, text="Проверить доступность", command=self._on_check_and_create).grid(row=6, column=1, padx=2, pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        f_read = ttk.LabelFrame(self, text="Список бронирований", padding=5)
        f_read.pack(fill="both", expand=True, pady=5)
        self._tree = ttk.Treeview(
            f_read, columns=("id", "user_id", "table_id", "date", "time", "guests", "status"), show="headings", height=6
        )
        self._tree.heading("id", text="ID")
        self._tree.heading("user_id", text="User ID")
        self._tree.heading("table_id", text="Table ID")
        self._tree.heading("date", text="Дата")
        self._tree.heading("time", text="Время")
        self._tree.heading("guests", text="Гостей")
        self._tree.heading("status", text="Статус")
        self._tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(f_read, orient="vertical", command=self._tree.yview)
        sb.pack(side="right", fill="y")
        self._tree.configure(yscrollcommand=sb.set)
        ttk.Button(f_read, text="Обновить", command=self._refresh).pack(pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        f_upd = ttk.LabelFrame(self, text="Обновить бронирование", padding=5)
        f_upd.pack(fill="x", pady=5)
        ttk.Label(f_upd, text="ID:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self._upd_id = ttk.Entry(f_upd, width=10)
        self._upd_id.grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(f_upd, text="Статус:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        status_options = [f"{i + 1}. {label}" for i, (_, label) in enumerate(backend.BOOKING_STATUSES)]
        self._upd_status = ttk.Combobox(f_upd, values=status_options, width=20)
        self._upd_status.grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(f_upd, text="Обновить", command=self._on_update).grid(row=2, column=1, pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        f_del = ttk.LabelFrame(self, text="Удалить бронирование", padding=5)
        f_del.pack(fill="x", pady=5)
        ttk.Label(f_del, text="ID:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self._del_id = ttk.Entry(f_del, width=10)
        self._del_id.grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(f_del, text="Удалить", command=self._on_delete).grid(row=1, column=1, pady=5)

        self._refresh()

    def _get_selected_table_id(self) -> Optional[int]:
        """Возвращает ID выбранного стола в форме создания бронирования."""
        sel = self._create_table_combo.get()
        if not sel or not self._create_table_display:
            return None
        try:
            idx = self._create_table_display.index(sel)
            return self._booking_tables_list[idx].id
        except (ValueError, IndexError):
            return None

    def _refresh_booking_tables_combo(self) -> None:
        """Обновляет список столов в выпадающем списке бронирования."""
        self._booking_tables_list = backend.read_restaurant_tables()
        self._create_table_display = [
            f"№{t.number} — {t.zone or '—'} ({t.capacity} мест)" for t in self._booking_tables_list
        ]
        self._create_table_combo["values"] = self._create_table_display
        if self._create_table_display:
            self._create_table_combo.current(0)

    def _on_create(self):
        try:
            user_id = int(self._create_user_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID пользователя должен быть числом.")
            return
        table_id = self._get_selected_table_id()
        if table_id is None:
            messagebox.showerror("Ошибка", "Выберите предпочтительный стол из списка.")
            return
        try:
            bdate = parse_date(self._create_date.get())
            btime = parse_time(self._create_time.get())
            guests = int(self._create_guests.get() or "1")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Проверьте данные: {e}")
            return
        if guests < 1:
            messagebox.showerror("Ошибка", "Гостей должно быть >= 1")
            return
        try:
            b = backend.create_booking(
                user_id=user_id,
                table_id=table_id,
                booking_date=bdate,
                booking_time=btime,
                guests_count=guests,
                comment=self._create_comment.get().strip() or None,
            )
            if b:
                messagebox.showinfo("Успех", f"Бронирование создано (ID={b.id})")
                self._create_comment.delete(0, tk.END)
                self._refresh()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать бронирование (проверьте user_id и table_id)")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_check_and_create(self):
        """Проверяет доступность и при успехе создаёт бронирование."""
        try:
            user_id = int(self._create_user_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID пользователя должен быть числом.")
            return
        table_id = self._get_selected_table_id()
        if table_id is None:
            messagebox.showerror("Ошибка", "Выберите предпочтительный стол из списка.")
            return
        try:
            bdate = parse_date(self._create_date.get())
            btime = parse_time(self._create_time.get())
            guests = int(self._create_guests.get() or "1")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Проверьте данные: {e}")
            return
        if guests < 1:
            messagebox.showerror("Ошибка", "Гостей должно быть >= 1")
            return
        try:
            available, msg = backend.check_table_availability(table_id, bdate, btime)
            if not available:
                messagebox.showwarning("Время занято", msg)
                return
            b = backend.create_booking(
                user_id=user_id,
                table_id=table_id,
                booking_date=bdate,
                booking_time=btime,
                guests_count=guests,
                comment=self._create_comment.get().strip() or None,
            )
            if b:
                messagebox.showinfo("Успех", f"Время свободно. Бронирование создано (ID={b.id})")
                self._create_comment.delete(0, tk.END)
                self._refresh()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать бронирование (проверьте user_id и table_id)")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _refresh(self):
        self._refresh_booking_tables_combo()
        for i in self._tree.get_children():
            self._tree.delete(i)
        for b in backend.read_bookings():
            self._tree.insert(
                "",
                tk.END,
                values=(
                    b.id,
                    b.user_id,
                    b.table_id,
                    str(b.booking_date),
                    str(b.booking_time)[:5],
                    b.guests_count,
                    backend.booking_status_label(b.status),
                ),
            )

    def _on_update(self):
        try:
            bid = int(self._upd_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID должен быть числом")
            return
        status_display = self._upd_status.get().strip()
        if not status_display:
            messagebox.showerror("Ошибка", "Укажите статус")
            return
        status_code = backend.booking_status_code_from_display(status_display)
        if not status_code:
            messagebox.showerror("Ошибка", "Неизвестный статус. Выберите из списка: 1. Подтверждено, 2. Отменено, 3. Завершено")
            return
        try:
            n = backend.update_booking(bid, status=status_code)
            if n > 0:
                messagebox.showinfo("Успех", f"Обновлено записей: {n}")
                self._refresh()
            else:
                messagebox.showwarning("Внимание", "Ничего не обновлено")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_delete(self):
        try:
            bid = int(self._del_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID должен быть числом")
            return
        if not messagebox.askyesno("Подтверждение", f"Удалить бронирование ID={bid}?"):
            return
        try:
            n = backend.delete_booking(bid)
            messagebox.showinfo("Успех", f"Удалено записей: {n}")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


def main():
    root = tk.Tk()
    root.title("Система бронирования ресторана")
    root.geometry("700x650")
    root.minsize(500, 400)

    try:
        backend.init_tables()
    except Exception as e:
        messagebox.showerror("Ошибка подключения", str(e))
        root.destroy()
        return

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=5, pady=5)

    notebook.add(UsersTab(notebook), text="Пользователи")
    notebook.add(TablesTab(notebook), text="Столы")
    notebook.add(BookingsTab(notebook), text="Бронирования")

    root.mainloop()


if __name__ == "__main__":
    main()
