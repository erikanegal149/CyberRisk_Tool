# main.py
# Точка входа — запуск приложения

import os
import customtkinter as ctk
from copy import deepcopy
from models.risk_model import CONTROLS
from views.dashboard import DashboardView
from views.controls import ControlsView
from views.risk_register import RiskRegisterView
from views.action_plan import ActionPlanView
from views.settings import SettingsView
from data.data_manager import save_data, load_data, export_to_excel


class App(ctk.CTk):
    def __init__(self):
        # Тёмная тема зафиксирована навсегда — вызываем до super().__init__()
        # чтобы окно создалось уже с правильной темой
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        super().__init__()

        # Настройки окна
        self.title("🛡️ CyberRisk Assessment Tool")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # Данные приложения
        self.controls = deepcopy(CONTROLS)
        self.risks = []
        self.settings = {}

        saved = load_data()
        if saved:
            self.controls = saved.get("controls", self.controls)
            self.risks = saved.get("risks", self.risks)
            self.settings = saved.get("settings", self.settings)

        self.build_ui()

    def build_ui(self):
        # Боковая панель навигации
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color="#16162a", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Логотип
        ctk.CTkLabel(
            self.sidebar, text="🛡️",
            font=ctk.CTkFont(size=40)
        ).pack(pady=(30, 0))

        ctk.CTkLabel(
            self.sidebar, text="CyberRisk\nAssessment Tool",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white", justify="center"
        ).pack(pady=(5, 30))

        # Кнопки навигации
        self.nav_buttons = {}
        nav_items = [
            ("🏠  Дашборд", "dashboard"),
            ("📋  Контроли", "controls"),
            ("⚠️  Реестр рисков", "risks"),
            ("📝  План действий", "actions"),
            ("⚙️  Настройки", "settings"),
        ]

        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color="#2d2d3f",
                anchor="w",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[key] = btn

               # Кнопка импорта
        ctk.CTkButton(
            self.sidebar, text="📂  Импорт Excel",
            font=ctk.CTkFont(size=12),
            fg_color="#9b59b6",
            hover_color="#7d3c98",
            command=self.import_excel
        ).pack(fill="x", padx=10, pady=3)

        # Кнопка экспорта
        ctk.CTkButton(
            self.sidebar, text="📊  Экспорт Excel",
            font=ctk.CTkFont(size=12),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.export_excel
        ).pack(fill="x", padx=10, pady=3)

        # Кнопка сохранения
        ctk.CTkButton(
            self.sidebar, text="💾  Сохранить",
            font=ctk.CTkFont(size=12),
            fg_color="#4a9eff",
            hover_color="#357abd",
            command=self.save
        ).pack(fill="x", padx=10, pady=3, side="bottom")

        # Основная область
        self.main_area = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=0)
        self.main_area.pack(side="right", fill="both", expand=True)

        # Показываем дашборд по умолчанию
        self.current_view = None
        self.show_view("dashboard")

    def show_view(self, view_name):
        # Убираем текущий экран
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Подсвечиваем активную кнопку
        for key, btn in self.nav_buttons.items():
            btn.configure(fg_color="#2d2d3f" if key == view_name else "transparent")

        # Показываем нужный экран
        if view_name == "dashboard":
            view = DashboardView(self.main_area, self.controls)
            # Сохраняем ссылку — on_controls_changed() вызовет view.refresh() напрямую
            self.dashboard_view = view

        elif view_name == "controls":
            view = ControlsView(
                self.main_area, self.controls,
                on_change_callback=self.on_controls_changed
            )

        elif view_name == "risks":
            # on_save_callback синхронизирует риски и сохраняет всё в Excel
            self.risk_view = RiskRegisterView(
                self.main_area, self.controls,
                on_save_callback=self.on_risks_changed
            )
            self.risk_view.risks = self.risks
            self.risk_view.refresh_table()
            view = self.risk_view

        elif view_name == "actions":
            view = ActionPlanView(self.main_area, self.controls)

        elif view_name == "settings":
            view = SettingsView(
                self.main_area, self.settings,
                on_save_callback=self.on_settings_saved
            )

        view.pack(fill="both", expand=True)
        self.current_view = view_name

    def on_controls_changed(self):
        """Вызывается при изменении оценок контролей"""
        self.mark_unsaved()
        self.save()
        # Если дашборд сейчас открыт — обновляем его на месте, без перехода
        if self.current_view == "dashboard" and hasattr(self, "dashboard_view"):
            self.dashboard_view.refresh(self.controls)

    def on_risks_changed(self):
        """Вызывается после добавления/изменения/удаления риска"""
        self.mark_unsaved()
        self.risks = self.risk_view.risks
        self.save()

    def on_settings_saved(self, new_settings):
        """Вызывается при сохранении настроек"""
        self.mark_unsaved()
        self.settings = new_settings
        self.save()

    def mark_unsaved(self):
        """Показывает * в заголовке когда есть несохранённые изменения"""
        self.title("🛡️ CyberRisk Assessment Tool *")

    def mark_saved(self):
        """Убирает * из заголовка после успешного сохранения"""
        self.title("🛡️ CyberRisk Assessment Tool")

    def save(self):
        """Сохраняет все данные"""
        if hasattr(self, "risk_view"):
            self.risks = self.risk_view.risks
        save_data(self.controls, self.risks, self.settings)
        self.mark_saved()

    def export_excel(self):
        """Экспортирует отчёт в Excel"""
        if hasattr(self, "risk_view"):
            self.risks = self.risk_view.risks
        filename = export_to_excel(self.controls, self.risks, self.settings)
        full_path = os.path.abspath(filename)
        # Показываем полный путь — пользователь сразу знает где искать файл
        dialog = ctk.CTkToplevel(self)
        dialog.title("Успех")
        dialog.geometry("520x180")
        dialog.configure(fg_color="#1e1e2e")
        dialog.grab_set()
        ctk.CTkLabel(
            dialog,
            text=f"✅ Отчёт сохранён:\n{full_path}",
            font=ctk.CTkFont(size=12),
            text_color="white",
            wraplength=480,
            justify="left"
        ).pack(pady=30, padx=20)
        ctk.CTkButton(
            dialog, text="OK",
            fg_color="#4a9eff",
            command=dialog.destroy
        ).pack()

    def import_excel(self):
        """Импортирует данные из Excel файла"""
        from tkinter import filedialog, messagebox
        filename = filedialog.askopenfilename(
            title="Выберите файл данных",
            filetypes=[("Excel файлы", "*.xlsx"), ("Все файлы", "*.*")]
        )
        if not filename:
            return

        # Предупреждаем до перезаписи — данные восстановить невозможно
        confirmed = messagebox.askyesno(
            title="Подтверждение импорта",
            message=(
                "Текущие данные будут заменены данными из выбранного файла.\n"
                "Это действие нельзя отменить. Продолжить?"
            )
        )
        if not confirmed:
            return

        try:
            from data.data_manager import load_data
            import shutil
            shutil.copy(filename, "cyberrisk_data.xlsx")
            saved = load_data()
            if saved:
                self.controls = saved.get("controls", self.controls)
                self.risks = saved.get("risks", self.risks)
                self.settings = saved.get("settings", self.settings)
                self.show_view("dashboard")

                dialog = ctk.CTkToplevel(self)
                dialog.title("Успех")
                dialog.geometry("350x150")
                dialog.configure(fg_color="#1e1e2e")
                dialog.grab_set()
                ctk.CTkLabel(
                    dialog,
                    text="✅ Данные успешно загружены!",
                    font=ctk.CTkFont(size=13),
                    text_color="white"
                ).pack(pady=30)
                ctk.CTkButton(
                    dialog, text="OK",
                    fg_color="#4a9eff",
                    command=dialog.destroy
                ).pack()
        except Exception as e:
            dialog = ctk.CTkToplevel(self)
            dialog.title("Ошибка")
            dialog.geometry("350x150")
            dialog.configure(fg_color="#1e1e2e")
            dialog.grab_set()
            ctk.CTkLabel(
                dialog,
                text=f"❌ Ошибка загрузки:\n{str(e)}",
                font=ctk.CTkFont(size=13),
                text_color="#e74c3c"
            ).pack(pady=30)
            ctk.CTkButton(
                dialog, text="OK",
                fg_color="#4a9eff",
                command=dialog.destroy
            ).pack()


if __name__ == "__main__":
    app = App()
    app.mainloop()