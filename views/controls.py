# views/controls.py
# Экран оценки 18 контролей

import customtkinter as ctk
from models.risk_model import CATEGORIES, get_risk_level


class ControlsView(ctk.CTkFrame):
    def __init__(self, parent, controls, on_change_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.controls = controls
        self.on_change_callback = on_change_callback
        self.configure(fg_color="#1e1e2e")
        self.build_ui()

    def build_ui(self):
        # Заголовок
        ctk.CTkLabel(
            self, text="📋 Оценка 18 контролей",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self, text="Оцените каждый контроль от 0 (не внедрён) до 5 (полностью внедрён)",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=(0, 20))

        # Список (slider, score_label, control) — нужен для кнопки сброса
        self._slider_refs = []

        # Кнопка сброса — пакуем с side="bottom" ДО scroll, чтобы pack зарезервировал место
        ctk.CTkButton(
            self, text="🔄 Сбросить все оценки",
            font=ctk.CTkFont(size=12),
            fg_color="#7d1a1a",
            hover_color="#a92222",
            command=self.reset_all
        ).pack(side="bottom", fill="x", padx=20, pady=(0, 15))

        # Скролл
        scroll = ctk.CTkScrollableFrame(self, fg_color="#1e1e2e")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 5))

        # Контроли по категориям
        for category in CATEGORIES:
            # Заголовок категории
            cat_frame = ctk.CTkFrame(scroll, fg_color="#2d2d3f", corner_radius=10)
            cat_frame.pack(fill="x", pady=(10, 5))

            ctk.CTkLabel(
                cat_frame, text=f"  {category}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#4a9eff"
            ).pack(anchor="w", padx=15, pady=10)

            # Контроли внутри категории
            category_controls = [c for c in self.controls if c["category"] == category]
            for control in category_controls:
                self.build_control_row(scroll, control)

    def build_control_row(self, parent, control):
        """Строит строку для одного контроля"""
        row_frame = ctk.CTkFrame(parent, fg_color="#2d2d3f", corner_radius=8)
        row_frame.pack(fill="x", pady=3)

        # Левая часть — информация
        info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)

        # Название и стандарт
        top_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        top_row.pack(fill="x")

        ctk.CTkLabel(
            top_row,
            text=f"{control['id']}. {control['name']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white", anchor="w"
        ).pack(side="left")

        ctk.CTkLabel(
            top_row,
            text=control["standard"],
            font=ctk.CTkFont(size=10),
            text_color="#4a9eff", anchor="e"
        ).pack(side="right")

        # Описание
        ctk.CTkLabel(
            info_frame,
            text=control["description"],
            font=ctk.CTkFont(size=11),
            text_color="#888888", anchor="w", wraplength=500
        ).pack(fill="x", pady=(3, 0))

        # Правая часть — оценка
        score_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        score_frame.pack(side="right", padx=15, pady=10)

        _, color = get_risk_level(control["score"])

        score_label = ctk.CTkLabel(
            score_frame,
            text=f"{control['score']}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=color, width=40
        )
        score_label.pack()

        # Слайдер оценки
        slider = ctk.CTkSlider(
            score_frame,
            from_=0, to=5,
            number_of_steps=10,
            width=150,
            button_color="#4a9eff",
            progress_color="#4a9eff"
        )
        slider.set(control["score"])
        slider.pack(pady=5)

        # Подписи слайдера
        labels_frame = ctk.CTkFrame(score_frame, fg_color="transparent")
        labels_frame.pack(fill="x")
        ctk.CTkLabel(labels_frame, text="0", font=ctk.CTkFont(size=9),
                     text_color="#888888").pack(side="left")
        ctk.CTkLabel(labels_frame, text="5", font=ctk.CTkFont(size=9),
                     text_color="#888888").pack(side="right")

        def on_slider_change(value, c=control, lbl=score_label):
            c["score"] = round(value, 1)
            _, col = get_risk_level(c["score"])
            lbl.configure(text=f"{c['score']}", text_color=col)
            self.on_change_callback()

        slider.configure(command=on_slider_change)
        # Сохраняем ссылки — reset_all() обойдёт этот список и обновит каждый виджет
        self._slider_refs.append((slider, score_label, control))

    def reset_all(self):
        """Сбрасывает все 18 контролей к 0 после подтверждения"""
        from tkinter import messagebox
        confirmed = messagebox.askyesno(
            "Сброс оценок",
            "Сбросить все 18 контролей к 0?\nЭто действие нельзя отменить."
        )
        if not confirmed:
            return
        _, color = get_risk_level(0)
        for slider, label, control in self._slider_refs:
            control["score"] = 0
            slider.set(0)
            label.configure(text="0", text_color=color)
        self.on_change_callback()