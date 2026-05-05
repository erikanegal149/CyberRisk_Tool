# views/action_plan.py
# План действий по обработке рисков

import customtkinter as ctk
from models.risk_model import get_risk_level


class ActionPlanView(ctk.CTkFrame):
    def __init__(self, parent, controls, **kwargs):
        super().__init__(parent, **kwargs)
        self.controls = controls
        self.configure(fg_color="#1e1e2e")
        self.build_ui()

    def build_ui(self):
        # Заголовок
        ctk.CTkLabel(
            self, text="📝 План действий",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self, text="Приоритизированный план по улучшению контролей кибербезопасности",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=(0, 20))

        # Скролл
        scroll = ctk.CTkScrollableFrame(self, fg_color="#1e1e2e")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Сортируем контроли по баллу (сначала самые критичные)
        sorted_controls = sorted(self.controls, key=lambda x: x["score"])

        for i, control in enumerate(sorted_controls):
            self.build_action_row(scroll, control, i + 1)

    def build_action_row(self, parent, control, priority):
        level, color = get_risk_level(control["score"])

        row = ctk.CTkFrame(parent, fg_color="#2d2d3f", corner_radius=8)
        row.pack(fill="x", pady=4)

        # Приоритет
        priority_label = ctk.CTkFrame(row, fg_color=color, corner_radius=6, width=40)
        priority_label.pack(side="left", padx=10, pady=10)
        priority_label.pack_propagate(False)
        ctk.CTkLabel(
            priority_label, text=str(priority),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(expand=True)

        # Информация
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=10)

        top = ctk.CTkFrame(info_frame, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top, text=control["name"],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white", anchor="w"
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=f"Балл: {control['score']} / 5",
            font=ctk.CTkFont(size=11),
            text_color=color, anchor="e"
        ).pack(side="right", padx=15)

        ctk.CTkLabel(
            info_frame, text=control["description"],
            font=ctk.CTkFont(size=11),
            text_color="#888888", anchor="w", wraplength=500
        ).pack(fill="x", pady=(3, 0))

        # Рекомендация
        recommendation = self.get_recommendation(control["score"])
        ctk.CTkLabel(
            info_frame,
            text=f"💡 {recommendation}",
            font=ctk.CTkFont(size=11),
            text_color="#4a9eff", anchor="w", wraplength=500
        ).pack(fill="x", pady=(5, 0))

        # Уровень риска
        ctk.CTkLabel(
            row, text=level,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=color, width=80
        ).pack(side="right", padx=15)

    def get_recommendation(self, score):
        if score == 0:
            return "Немедленно внедрить контроль — риск не покрыт"
        elif score < 2:
            return "Критически важно улучшить — высокий уровень риска"
        elif score < 3:
            return "Требуется улучшение в ближайшее время"
        elif score < 4:
            return "Контроль частично внедрён — рекомендуется усилить"
        else:
            return "Контроль хорошо внедрён — поддерживать текущий уровень"

    def refresh(self, controls):
        self.controls = controls
        for widget in self.winfo_children():
            widget.destroy()
        self.build_ui()