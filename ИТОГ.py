import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import json
import os

class QuoteGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных цитат")
        self.root.geometry("850x650")
        self.root.minsize(700, 500)

        # 1. Предопределённый список цитат
        self.quotes = [
            {"text": "Будь собой, прочие роли уже заняты.", "author": "Оскар Уайльд", "topic": "Личность"},
            {"text": "Жизнь — это то, что случается с тобой, пока ты строишь другие планы.", "author": "Джон Леннон", "topic": "Жизнь"},
            {"text": "Успех — это способность идти от неудачи к неудаче, не теряя энтузиазма.", "author": "Уинстон Черчилль", "topic": "Успех"},
            {"text": "Единственный способ делать великую работу — любить то, что вы делаете.", "author": "Стив Джобс", "topic": "Работа"},
            {"text": "Образование — это самое мощное оружие, которое вы можете использовать, чтобы изменить мир.", "author": "Нельсон Мандела", "topic": "Образование"},
            {"text": "Свобода — это то, что вы делаете с тем, что вам сделали.", "author": "Жан-Поль Сартр", "topic": "Философия"}
        ]
        self.history = []
        self.history_file = "history.json"

        self._build_ui()
        self._load_history()

    def _build_ui(self):
        # --- Фильтры ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Автор:").pack(side="left", padx=5)
        self.author_var = tk.StringVar(value="Все")
        self.author_cb = ttk.Combobox(filter_frame, textvariable=self.author_var, state="readonly", width=18)
        self.author_cb.pack(side="left", padx=5)

        ttk.Label(filter_frame, text="Тема:").pack(side="left", padx=5)
        self.topic_var = tk.StringVar(value="Все")
        self.topic_cb = ttk.Combobox(filter_frame, textvariable=self.topic_var, state="readonly", width=18)
        self.topic_cb.pack(side="left", padx=5)

        self._update_filter_options()

        ttk.Button(filter_frame, text="Применить фильтр", command=self._generate).pack(side="right", padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self._reset_filters).pack(side="right", padx=5)

        # --- Отображение текущей цитаты ---
        display_frame = ttk.Frame(self.root)
        display_frame.pack(fill="x", padx=10, pady=10)

        self.current_label = ttk.Label(display_frame, text="Нажмите «Сгенерировать», чтобы получить цитату", 
                                       wraplength=750, justify="center", font=("Segoe UI", 14, "bold"))
        self.current_label.pack()

        # --- Кнопки управления ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="🎲 Сгенерировать цитату", command=self._generate).pack(side="left", expand=True, padx=5, fill="x")
        ttk.Button(btn_frame, text="➕ Добавить цитату", command=self._add_new_quote).pack(side="left", expand=True, padx=5, fill="x")
        ttk.Button(btn_frame, text="💾 Сохранить историю", command=self._save_history).pack(side="left", expand=True, padx=5, fill="x")
        ttk.Button(btn_frame, text="🗑 Очистить историю", command=self._clear_history).pack(side="left", expand=True, padx=5, fill="x")

        # --- История (Treeview) ---
        hist_frame = ttk.LabelFrame(self.root, text="📜 История генераций")
        hist_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("author", "topic", "text")
        self.history_tree = ttk.Treeview(hist_frame, columns=columns, show="headings")
        self.history_tree.heading("author", text="Автор")
        self.history_tree.heading("topic", text="Тема")
        self.history_tree.heading("text", text="Цитата")
        self.history_tree.column("author", width=140)
        self.history_tree.column("topic", width=110)
        self.history_tree.column("text", width=500)
        self.history_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(hist_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)

    def _update_filter_options(self):
        authors = sorted(set(q["author"] for q in self.quotes))
        topics = sorted(set(q["topic"] for q in self.quotes))
        self.author_cb["values"] = ["Все"] + authors
        self.topic_cb["values"] = ["Все"] + topics

    def _reset_filters(self):
        self.author_var.set("Все")
        self.topic_var.set("Все")

    def _get_filtered_quotes(self):
        filtered = self.quotes
        if self.author_var.get() != "Все":
            filtered = [q for q in filtered if q["author"] == self.author_var.get()]
        if self.topic_var.get() != "Все":
            filtered = [q for q in filtered if q["topic"] == self.topic_var.get()]
        return filtered

    # 2. Случайная выборка
    def _generate(self):
        filtered = self._get_filtered_quotes()
        if not filtered:
            messagebox.showwarning("Нет данных", "Цитаты по выбранным фильтрам не найдены. Добавьте новую или сбросьте фильтры.")
            return
        
        quote = random.choice(filtered)
        self.current_label.config(text=f"«{quote['text']}»\n— {quote['author']} | Тема: {quote['topic']}")
        
        # 3. Добавление в историю
        self.history.append(quote)
        self._refresh_history_display()

    def _refresh_history_display(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for q in self.history:
            self.history_tree.insert("", "end", values=(q["author"], q["topic"], q["text"]))
        self.history_tree.yview_moveto(1.0)

    # 6. Валидация ввода
    def _add_new_quote(self):
        text = simpledialog.askstring("Новая цитата", "Введите текст цитаты:")
        if not text or not text.strip():
            messagebox.showerror("Ошибка ввода", "Текст цитаты не может быть пустым.")
            return
            
        author = simpledialog.askstring("Новая цитата", "Введите автора:")
        if not author or not author.strip():
            messagebox.showerror("Ошибка ввода", "Автор не может быть пустым.")
            return
            
        topic = simpledialog.askstring("Новая цитата", "Введите тему:")
        if not topic or not topic.strip():
            messagebox.showerror("Ошибка ввода", "Тема не может быть пустой.")
            return

        new_quote = {"text": text.strip(), "author": author.strip(), "topic": topic.strip()}
        self.quotes.append(new_quote)
        self._update_filter_options()
        messagebox.showinfo("Успех", "Цитата успешно добавлена в общую базу!")

    # 5. Сохранение в JSON
    def _save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранение", f"История ({len(self.history)} записей) сохранена в {self.history_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю:\n{e}")

    # 5. Загрузка из JSON
    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        self.history = loaded
                        self._refresh_history_display()
            except (json.JSONDecodeError, Exception) as e:
                messagebox.showwarning("Загрузка", f"Файл истории повреждён или пуст. Начинаем с чистой истории.\n({e})")

    def _clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю генераций?"):
            self.history = []
            self._refresh_history_display()
            messagebox.showinfo("Готово", "История очищена.")

if __name__ == "__main__":
    root = tk.Tk()
    # Применяем тему для современного вида
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    app = QuoteGeneratorApp(root)
    root.mainloop()