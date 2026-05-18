# CyberRisk Assessment Tool

## О проекте
Десктопное приложение для менеджмента киберрисков на основе стандартов ISO/IEC 27005:2022 и ISO/IEC 27032:2023. Дипломная работа.

## Технологии
- Python 3.12.8
- CustomTkinter 5.2.2 — графический интерфейс
- Matplotlib — радарная диаграмма
- Openpyxl — чтение/запись Excel
- Pillow — графические элементы

## Архитектура (MVC)
- models/risk_model.py — 18 контролей, логика расчёта риска
- views/ — 5 экранов (dashboard, controls, risk_register, action_plan, settings)
- data/data_manager.py — сохранение/загрузка Excel
- utils/charts.py — радарная диаграмма
- main.py — контроллер, навигация

## Хранилище данных
Файл cyberrisk_data.xlsx, три листа: Настройки, Контроли, Риски

## Запуск
cd C:\Users\erika\CyberRisk_Tool
venv\Scripts\activate
python main.py


