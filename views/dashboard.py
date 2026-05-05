# views/dashboard.py
# Главный экран с радаром и общей статистикой

import customtkinter as ctk
from utils.charts import create_radar_chart, update_radar_chart
from models.risk_model import get_overall_score, get_risk_level, get_category_scores, CATEGORIES


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controls, **kwargs):
        super().__init__(parent, **kwargs)
        self.controls = controls
        self.configure(fg_color="#1e1e2e")
        self.build_ui()

    def build_ui(self):
        # Заголовок
        title = ctk.CTkLabel(
            self, text="🛡️ CyberRisk Assessment Tool",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        )
        title.pack(pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self, text="Менеджмент киберрисков согласно ISO/IEC 27005 и ISO/IEC 27032",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        subtitle.pack(pady=(0, 20))

        # Основной контейнер (радар + статистика)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20)

        # Левая часть — радар
        # self.radar_canvas хранится как атрибут, чтобы refresh() мог передать его в update_radar_chart()
        left_frame = ctk.CTkFrame(main_frame, fg_color="#2d2d3f", corner_radius=12)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.radar_canvas = create_radar_chart(left_frame, self.controls)
        self.radar_canvas.get_tk_widget().pack(padx=10, pady=10)

        # Правая часть — статистика
        # self.right_frame хранится как атрибут, чтобы _build_stats() могла его очистить и перестроить
        self.right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", padx=(10, 0))

        self._build_stats()

    def _build_stats(self):
        """Строит (или перестраивает) правую панель со статистикой.
        Вызывается из build_ui() при первичном рендере и из refresh() при обновлении."""
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Общий балл
        overall = get_overall_score(self.controls)
        level, color = get_risk_level(overall)

        score_frame = ctk.CTkFrame(self.right_frame, fg_color="#2d2d3f", corner_radius=12)
        score_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            score_frame, text="Общий балл",
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        ).pack(pady=(15, 0))

        ctk.CTkLabel(
            score_frame, text=f"{overall} / 5.0",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=color
        ).pack()

        ctk.CTkLabel(
            score_frame, text=f"Уровень риска: {level}",
            font=ctk.CTkFont(size=12),
            text_color=color
        ).pack(pady=(0, 15))

        # Статистика по категориям
        cat_frame = ctk.CTkFrame(self.right_frame, fg_color="#2d2d3f", corner_radius=12)
        cat_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            cat_frame, text="Баллы по категориям",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        ).pack(pady=(15, 10))

        cat_scores = get_category_scores(self.controls)
        for category, score in cat_scores.items():
            _, color = get_risk_level(score)
            row = ctk.CTkFrame(cat_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)

            ctk.CTkLabel(
                row, text=category,
                font=ctk.CTkFont(size=11),
                text_color="white", anchor="w"
            ).pack(side="left")

            ctk.CTkLabel(
                row, text=f"{score}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=color, anchor="e"
            ).pack(side="right")

            progress = ctk.CTkProgressBar(cat_frame, height=6, corner_radius=3)
            progress.configure(progress_color=color, fg_color="#1e1e2e")
            progress.set(score / 5)
            progress.pack(fill="x", padx=15, pady=(0, 5))

        # Топ-3 критических контроля
        risk_frame = ctk.CTkFrame(self.right_frame, fg_color="#2d2d3f", corner_radius=12)
        risk_frame.pack(fill="x")

        ctk.CTkLabel(
            risk_frame, text="⚠️ Критические контроли",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        ).pack(pady=(15, 10))

        sorted_controls = sorted(self.controls, key=lambda x: x["score"])[:3]
        for control in sorted_controls:
            _, color = get_risk_level(control["score"])
            ctk.CTkLabel(
                risk_frame,
                text=f"• {control['name']} — {control['score']}",
                font=ctk.CTkFont(size=11),
                text_color=color, anchor="w"
            ).pack(fill="x", padx=15, pady=2)

        ctk.CTkLabel(risk_frame, text="").pack(pady=5)

    def refresh(self, controls):
        """Обновляет дашборд без пересоздания всего экрана.
        Радар обновляется через update_radar_chart(), статистика — через _build_stats()."""
        self.controls = controls
        # update_radar_chart сам удаляет старый холст, создаёт новый и возвращает его
        self.radar_canvas = update_radar_chart(self.radar_canvas, self.controls)
        self._build_stats()