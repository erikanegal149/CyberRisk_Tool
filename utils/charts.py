# utils/charts.py
# Радар рисков и графики

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from models.risk_model import CATEGORIES, get_category_scores, get_risk_level


def create_radar_chart(parent_frame, controls):
    """Создаёт радар рисков и встраивает его в окно приложения"""

    scores = get_category_scores(controls)
    values = [scores[cat] for cat in CATEGORIES]

    # Замыкаем радар (первая точка повторяется в конце)
    values += values[:1]
    N = len(CATEGORIES)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # Создаём фигуру
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    # Зона допустимого риска (зелёная область от 3 до 5)
    safe_values = [3] * N + [3]
    ax.fill(angles, safe_values, alpha=0.1, color="#2ecc71")

    # Основной радар
    ax.plot(angles, values, color="#4a9eff", linewidth=2)
    ax.fill(angles, values, alpha=0.25, color="#4a9eff")

    # Точки на радаре с цветом по уровню риска
    for i, (angle, value) in enumerate(zip(angles[:-1], values[:-1])):
        _, color = get_risk_level(value)
        ax.plot(angle, value, "o", color=color, markersize=8)

    # Настройка осей
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(CATEGORIES, size=8, color="white")
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], color="grey", size=7)
    ax.grid(color="grey", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.spines["polar"].set_color("grey")

    # Заголовок
    ax.set_title("Радар киберрисков", color="white", size=13, pad=15)

    # Легенда
    low = mpatches.Patch(color="#2ecc71", label="Низкий риск (4-5)")
    med = mpatches.Patch(color="#f39c12", label="Средний риск (2.5-4)")
    high = mpatches.Patch(color="#e74c3c", label="Высокий риск (0-2.5)")
    ax.legend(handles=[low, med, high], loc="upper right",
              bbox_to_anchor=(1.3, 1.1), fontsize=7,
              facecolor="#2d2d3f", labelcolor="white")

    plt.tight_layout()

    # Встраиваем в tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    # Холст уже держит данные фигуры внутри себя — сама фигура matplotlib больше не нужна
    plt.close(fig)
    return canvas


def update_radar_chart(canvas, controls):
    """Обновляет радар при изменении оценок — возвращает новый canvas"""
    # Сохраняем родительский фрейм ДО уничтожения виджета
    parent = canvas.get_tk_widget().master
    canvas.get_tk_widget().destroy()
    plt.close("all")
    # Создаём новый холст в том же родителе и сразу его размещаем
    new_canvas = create_radar_chart(parent, controls)
    new_canvas.get_tk_widget().pack(padx=10, pady=10)
    return new_canvas