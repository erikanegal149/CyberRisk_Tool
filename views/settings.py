# views/settings.py
# Настройки организации

import customtkinter as ctk


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, app_settings, on_save_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.app_settings = app_settings
        self.on_save_callback = on_save_callback
        self.configure(fg_color="#1e1e2e")
        self.build_ui()

    def build_ui(self):
        # Заголовок
        ctk.CTkLabel(
            self, text="⚙️ Настройки",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self, text="Настройки организации и приложения",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=(0, 30))

        # Форма настроек
        form = ctk.CTkFrame(self, fg_color="#2d2d3f", corner_radius=12)
        form.pack(padx=40, fill="x")

        ctk.CTkLabel(
            form, text="Информация об организации",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=(20, 15))

        self.fields = {}

        for label, key, placeholder in [
            ("Название организации", "org_name", "Например: ООО Ромашка"),
            ("Отрасль", "industry", "Например: Финансы, IT, Медицина"),
            ("Ответственный", "responsible", "ФИО ответственного за ИБ"),
            ("Дата оценки", "date", "Например: 04.03.2026"),
        ]:
            ctk.CTkLabel(
                form, text=label,
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            ).pack(anchor="w", padx=20)

            entry = ctk.CTkEntry(
                form, width=400,
                placeholder_text=placeholder,
                fg_color="#1e1e2e",
                border_color="#4a9eff"
            )
            entry.pack(anchor="w", padx=20, pady=(0, 15))

            # Заполняем текущими значениями
            if self.app_settings.get(key):
                entry.insert(0, self.app_settings[key])

            self.fields[key] = entry

        # Кнопка сохранения
        ctk.CTkButton(
            self, text="💾 Сохранить настройки",
            font=ctk.CTkFont(size=13),
            fg_color="#4a9eff",
            hover_color="#357abd",
            command=self.save_settings
        ).pack(pady=20)

        # Статус сохранения
        self.status_label = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=12),
            text_color="#2ecc71"
        )
        self.status_label.pack()

    def save_settings(self):
        for key, entry in self.fields.items():
            self.app_settings[key] = entry.get()
        self.on_save_callback(self.app_settings)
        self.status_label.configure(text="✅ Настройки сохранены!")