# views/risk_register.py
# Реестр рисков

import customtkinter as ctk


class RiskRegisterView(ctk.CTkFrame):
    # on_save_callback — вызывается после добавления риска, чтобы сохранить данные в Excel
    def __init__(self, parent, controls, on_save_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controls = controls
        self.on_save_callback = on_save_callback
        self.risks = []
        self.configure(fg_color="#1e1e2e")
        self.build_ui()

    def build_ui(self):
        # Заголовок
        ctk.CTkLabel(
            self, text="⚠️ Реестр рисков",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self, text="Документирование и отслеживание киберрисков организации",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=(0, 20))

        # Кнопка добавления риска
        ctk.CTkButton(
            self, text="+ Добавить риск",
            font=ctk.CTkFont(size=13),
            fg_color="#4a9eff",
            hover_color="#357abd",
            command=self.add_risk_dialog
        ).pack(pady=(0, 15))

        # Таблица рисков
        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color="#1e1e2e"
        )
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Заголовок и строки строятся вместе в refresh_table()
        self.refresh_table()

    # Эталонные ширины колонок — одинаковы для заголовка и каждой строки данных
    _COL_WIDTHS = [40, 220, 110, 110, 90, 120, 40]

    @staticmethod
    def _truncate(text, max_chars=25):
        """Обрезает текст с '…' если длиннее max_chars — предотвращает растяжение колонки."""
        return text if len(text) <= max_chars else text[:max_chars - 1] + "…"

    def build_table_header(self):
        header = ctk.CTkFrame(self.table_frame, fg_color="#2d2d3f", corner_radius=8)
        header.pack(fill="x", pady=(0, 5))

        # Последняя колонка "" — резерв под кнопку удаления
        headers = ["ID", "Название риска", "Вероятность", "Ущерб", "Уровень", "Статус", ""]

        for h, w in zip(headers, self._COL_WIDTHS):
            ctk.CTkLabel(
                header, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#4a9eff",
                width=w, anchor="w",
                wraplength=0          # запрет переноса текста в заголовке
            ).pack(side="left", padx=5, pady=10)

    def refresh_table(self):
        # Сносим всё и перестраиваем заголовок заново —
        # безопаснее чем пытаться пропустить первый виджет во время итерации
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.build_table_header()

        if not self.risks:
            ctk.CTkLabel(
                self.table_frame,
                text="Рисков пока нет. Нажмите '+ Добавить риск'",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            ).pack(pady=30)
            return

        for risk in self.risks:
            self.build_risk_row(risk)

    def build_risk_row(self, risk):
        row = ctk.CTkFrame(self.table_frame, fg_color="#2d2d3f", corner_radius=8)
        row.pack(fill="x", pady=2)

        def risk_color(text):
            if text == "Критический":
                return "#8b0000"   # тёмно-красный
            elif text in ["Высокий", "Высокое", "Очень высокое"]:
                return "#e74c3c"   # красный
            elif text in ["Средний", "Среднее"]:
                return "#f39c12"   # оранжевый
            else:                  # Низкий, Низкое, Очень низкое
                return "#2ecc71"   # зелёный

        def prob_color(text):
            if text == "Очень высокая":
                return "#8b0000"   # тёмно-красный
            elif text == "Высокая":
                return "#f44336"   # красный
            elif text == "Средняя":
                return "#FF9800"   # оранжевый
            else:                  # Низкая, Очень низкая
                return "#4CAF50"   # зелёный

        # Статичные колонки — ширины берём из _COL_WIDTHS чтобы совпадали с заголовком.
        # Название обрезается через _truncate(): длинный текст не растягивает колонку.
        w = self._COL_WIDTHS
        static_values = [
            (str(risk["id"]),                w[0], "white"),
            (self._truncate(risk["name"]),   w[1], "white"),
            (risk["probability"],            w[2], prob_color(risk["probability"])),
            (risk["impact"],                 w[3], risk_color(risk["impact"])),
            (risk["level_text"],             w[4], risk_color(risk["level_text"])),
        ]

        for val, width, text_color in static_values:
            ctk.CTkLabel(
                row, text=val,
                font=ctk.CTkFont(size=11),
                text_color=text_color,
                width=width, anchor="w",
                wraplength=0          # запрет переноса — строка всегда одной высоты
            ).pack(side="left", padx=5, pady=8)

        # Колонка «Статус» — выпадающий список, меняет статус без пересоздания строки
        def on_status_change(new_status, r=risk):
            r["status"] = new_status
            if self.on_save_callback:
                self.on_save_callback()

        status_menu = ctk.CTkOptionMenu(
            row,
            values=["Открыт", "В обработке", "Закрыт", "Принят"],
            command=on_status_change,
            width=120,
            fg_color="#1e1e2e",
            button_color="#4a9eff",
            font=ctk.CTkFont(size=11)
        )
        status_menu.set(risk["status"])
        status_menu.pack(side="left", padx=5, pady=6)

        # Кнопка удаления — с диалогом подтверждения
        def delete_risk(r=risk):
            from tkinter import messagebox
            confirmed = messagebox.askyesno(
                "Удаление риска",
                f"Удалить риск '{r['name']}'?\nЭто действие нельзя отменить."
            )
            if not confirmed:
                return
            self.risks.remove(r)
            # Перенумеровываем ID чтобы не оставалось пропусков
            for i, item in enumerate(self.risks, 1):
                item["id"] = i
            self.refresh_table()
            if self.on_save_callback:
                self.on_save_callback()

        ctk.CTkButton(
            row, text="🗑️",
            width=36, height=28,
            fg_color="#7d1a1a",
            hover_color="#a92222",
            font=ctk.CTkFont(size=13),
            command=delete_risk
        ).pack(side="left", padx=5, pady=6)

    def add_risk_dialog(self):
        """Диалог добавления нового риска"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Добавить риск")
        dialog.geometry("450x500")
        dialog.configure(fg_color="#1e1e2e")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Новый риск",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=20)

        # Поля ввода
        fields = {}

        for label, key in [
            ("Название риска", "name"),
            ("Описание", "description"),
        ]:
            ctk.CTkLabel(dialog, text=label,
                         text_color="#888888").pack(anchor="w", padx=20)
            entry = ctk.CTkEntry(dialog, width=400, fg_color="#2d2d3f",
                                 border_color="#4a9eff")
            entry.pack(padx=20, pady=(0, 10))
            fields[key] = entry

        # Вероятность (1–5: Очень низкая → Очень высокая)
        ctk.CTkLabel(dialog, text="Вероятность",
                     text_color="#888888").pack(anchor="w", padx=20)
        prob_var = ctk.StringVar(value="Средняя")
        prob_menu = ctk.CTkOptionMenu(
            dialog,
            values=["Очень низкая", "Низкая", "Средняя", "Высокая", "Очень высокая"],
            variable=prob_var, fg_color="#2d2d3f",
            button_color="#4a9eff"
        )
        prob_menu.pack(padx=20, pady=(0, 10), anchor="w")

        # Ущерб (воздействие, 1–5: Очень низкое → Очень высокое)
        ctk.CTkLabel(dialog, text="Ущерб",
                     text_color="#888888").pack(anchor="w", padx=20)
        impact_var = ctk.StringVar(value="Среднее")
        impact_menu = ctk.CTkOptionMenu(
            dialog,
            values=["Очень низкое", "Низкое", "Среднее", "Высокое", "Очень высокое"],
            variable=impact_var, fg_color="#2d2d3f",
            button_color="#4a9eff"
        )
        impact_menu.pack(padx=20, pady=(0, 10), anchor="w")

        # Статус
        ctk.CTkLabel(dialog, text="Статус",
                     text_color="#888888").pack(anchor="w", padx=20)
        status_var = ctk.StringVar(value="Открыт")
        status_menu = ctk.CTkOptionMenu(
            dialog, values=["Открыт", "В обработке", "Закрыт"],
            variable=status_var, fg_color="#2d2d3f",
            button_color="#4a9eff"
        )
        status_menu.pack(padx=20, pady=(0, 20), anchor="w")

        def save_risk():
            prob_map = {
                "Очень низкая": 1, "Низкая": 2, "Средняя": 3,
                "Высокая": 4, "Очень высокая": 5
            }
            impact_map = {
                "Очень низкое": 1, "Низкое": 2, "Среднее": 3,
                "Высокое": 4, "Очень высокое": 5
            }
            # Уровень = Вероятность × Воздействие (диапазон 1–25)
            level = prob_map[prob_var.get()] * impact_map[impact_var.get()]
            if level <= 4:
                level_text = "Низкий"
            elif level <= 9:
                level_text = "Средний"
            elif level <= 16:
                level_text = "Высокий"
            else:
                level_text = "Критический"

            self.risks.append({
                "id": len(self.risks) + 1,
                "name": fields["name"].get() or "Без названия",
                "description": fields["description"].get(),
                "probability": prob_var.get(),
                "impact": impact_var.get(),
                "level": level,
                "level_text": level_text,
                "status": status_var.get()
            })
            dialog.destroy()
            self.refresh_table()
            # Сохраняем в Excel сразу после добавления риска
            if self.on_save_callback:
                self.on_save_callback()

        ctk.CTkButton(
            dialog, text="Сохранить",
            fg_color="#4a9eff", hover_color="#357abd",
            command=save_risk
        ).pack(pady=10)