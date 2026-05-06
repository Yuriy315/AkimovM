import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random, json, os

# --- Настройки ---
DATA_FILES = {
    'history': 'tasks_history.json',
    'custom': 'custom_tasks.json'
}
CATEGORIES = ["Учёба", "Спорт", "Работа"]
PREDEFINED_TASKS = {
    "Учёба": ["Прочитать статью", "Решить 5 задач", "Посмотреть обучающее видео"],
    "Спорт": ["Сделать зарядку", "Пробежать 3 км", "Сделать 50 приседаний"],
    "Работа": ["Проверить почту", "Составить отчёт", "Провести созвон"]
}


# ------------------


class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.history = []
        self.custom_tasks = {cat: [] for cat in CATEGORIES}

        self.load_data()
        self.create_widgets()

    def load_data(self):
        """Загрузка истории и кастомных задач из JSON-файлов."""
        for key, filename in DATA_FILES.items():
            if not os.path.exists(filename):
                # Создаём файл, если его нет (для history это пустой список)
                with open(filename, 'w', encoding='utf-8') as f:
                    if key == 'history':
                        json.dump([], f)
                    else:
                        json.dump(self.custom_tasks, f, ensure_ascii=False, indent=2)

        with open(DATA_FILES['history'], 'r', encoding='utf-8') as f:
            self.history = json.load(f)

        with open(DATA_FILES['custom'], 'r', encoding='utf-8') as f:
            self.custom_tasks = json.load(f)

    def save_data(self):
        """Сохранение данных в JSON-файлы."""
        with open(DATA_FILES['history'], 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        with open(DATA_FILES['custom'], 'w', encoding='utf-8') as f:
            json.dump(self.custom_tasks, f, ensure_ascii=False, indent=2)

    def create_widgets(self):
        # --- Верхняя панель: Генерация ---
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, fill='x')

        tk.Label(top_frame, text="Категория:").pack(side='left')

        # Список категорий (включая кастомные задачи)
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.category_dropdown = ttk.Combobox(top_frame, textvariable=self.category_var,
                                              values=CATEGORIES, state="readonly", width=15)
        self.category_dropdown.pack(side='left', padx=5)

        self.task_display = tk.Entry(top_frame, width=40, state='readonly', font=('Arial', 12))
        self.task_display.pack(side='left', padx=10, expand=True, fill='x')

        btn_gen = tk.Button(top_frame, text="Сгенерировать задачу", command=self.generate_task)
        btn_gen.pack(side='left')

        # --- Средняя панель: Добавление новой задачи ---
        mid_frame = tk.Frame(self.root)
        mid_frame.pack(pady=10, fill='x')

        tk.Label(mid_frame, text="Добавить новую задачу:").pack(anchor='w')

        self.new_task_entry = tk.Entry(mid_frame, width=30)
        self.new_task_entry.pack(side='left', padx=5)

        # Выпадающий список для категории новой задачи (динамический)
        self.new_category_var = tk.StringVar()
        self.update_new_category_dropdown()

        self.new_category_dropdown = ttk.Combobox(mid_frame,
                                                  textvariable=self.new_category_var,
                                                  values=self.category_dropdown['values'],
                                                  state="readonly", width=15)
        self.new_category_dropdown.pack(side='left', padx=5)

        btn_add = tk.Button(mid_frame, text="Добавить", command=self.add_custom_task)
        btn_add.pack(side='left', padx=5)

        # --- Нижняя панель: История и Фильтр ---
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10, fill='both', expand=True)

        # Фильтр по категории для истории
        filter_frame = tk.Frame(bottom_frame)
        filter_frame.pack(fill='x')

        tk.Label(filter_frame, text="Фильтр истории:").pack(side='left')

        self.filter_var = tk.StringVar(value="Все")
        filter_options = ["Все"] + CATEGORIES + ["Пользовательские"]
        self.filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                            values=filter_options, state="readonly", width=15)
        self.filter_dropdown.pack(side='left', padx=5)

        btn_clear_history = tk.Button(filter_frame, text="Очистить историю", fg="red",
                                      command=self.clear_history)
        btn_clear_history.pack(side='right')

        # Список истории (с прокруткой)
        self.history_listbox = tk.Listbox(bottom_frame, height=12, width=70,
                                          font=('Arial', 10))
        self.history_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(bottom_frame, command=self.history_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        # Привязка события изменения фильтра для обновления списка
        self.filter_var.trace_add('write', lambda *args: self.update_history_list())

    def update_new_category_dropdown(self):
        """Обновляет список категорий в поле добавления новой задачи."""
        all_categories = CATEGORIES + list(self.custom_tasks.keys())
        unique_categories = list(dict.fromkeys(all_categories))  # Сохраняем порядок, убираем дубликаты
        self.new_category_dropdown['values'] = unique_categories

    def generate_task(self):
        """Генерирует случайную задачу на основе выбранной категории."""
        category = self.category_var.get()

        if category in CATEGORIES:
            task_list = PREDEFINED_TASKS[category] + self.custom_tasks.get(category, [])
            if not task_list:
                messagebox.showwarning("Пусто", f"В категории '{category}' нет задач.")
                return
            task = random.choice(task_list)

            # Добавляем в историю с пометкой источника (для фильтра)
            source_tag = "Предопределённая" if task in PREDEFINED_TASKS[category] else "Пользовательская"
            self.history.append({"task": task, "category": category, "source": source_tag})

            self.save_data()
            self.update_history_list()

            self.task_display.config(state='normal')
            self.task_display.delete(0, 'end')
            self.task_display.insert(0, task)
            self.task_display.config(state='readonly')

    def add_custom_task(self):
        """Добавляет новую задачу от пользователя."""
        task_text = self.new_task_entry.get().strip()
        category = self.new_category_var.get()

        if not task_text:
            messagebox.showerror("Ошибка", "Поле задачи не может быть пустым.")
            return

        if category not in CATEGORIES + list(self.custom_tasks.keys()):
            messagebox.showerror("Ошибка", "Выберите категорию из списка.")
            return

        # Создаём категорию, если её нет (для пользовательских категорий)
        if category not in self.custom_tasks:
            self.custom_tasks[category] = []

        if task_text in self.custom_tasks[category]:
            messagebox.showwarning("Дубликат", "Такая задача уже есть в этой категории.")
            return

        self.custom_tasks[category].append(task_text)

        # Обновляем выпадающие списки категорий во всём приложении
        all_categories_for_dropdowns = CATEGORIES + list(self.custom_tasks.keys())
        unique_cats_for_dropdowns = list(dict.fromkeys(all_categories_for_dropdowns))

        self.category_dropdown['values'] = unique_cats_for_dropdowns
        self.update_new_category_dropdown()

        self.save_data()

        messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена в категорию '{category}'.")
        self.new_task_entry.delete(0, 'end')

    def update_history_list(self):
        """Обновляет список истории в зависимости от выбранного фильтра."""
        filter_value = self.filter_var.get()

        self.history_listbox.delete(0, 'end')

        for item in reversed(self.history):  # Показываем новые задачи сверху
            show_item = False

            if filter_value == "Все":
                show_item = True
            elif filter_value in CATEGORIES and item['category'] == filter_value:
                show_item = True
            elif filter_value == "Пользовательские" and item['source'] == "Пользовательская":
                show_item = True

            if show_item:
                display_text = f"[{item['category']}] {item['task']} ({item['source']})"
                self.history_listbox.insert('end', display_text)

    def clear_history(self):
        """Очищает историю сгенерированных задач."""
        if messagebox.askyesno("Подтвердить", "Вы уверены, что хотите очистить всю историю?"):
            self.history.clear()
            self.save_data()
            self.update_history_list()

    def on_closing(self):
        """Сохраняет данные при закрытии окна."""
        self.save_data()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()