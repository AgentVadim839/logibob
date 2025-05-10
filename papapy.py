from customtkinter import *
from socket import *
from datetime import datetime
import threading
import winsound
import random
# Встановлюємо системну тему (світла/темна залежно від ОС)
set_appearance_mode("System")
# Встановлюємо синю колірну тему за замовчуванням
set_default_color_theme("blue")


# Основний клас нашого чату, який наслідує головне вікно CTk
class MainWindow(CTk):
    def __init__(self):
        super().__init__()  # Ініціалізуємо батьківський клас
        self.colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "gray"]

        self.message_count = 0
        self.title("Chat")  # Назва вікна
        self.geometry("800x600")  # Початковий розмір вікна
        self.minsize(500, 400)  # Мінімальний розмір, щоб не стиснути занадто

        self.username = "Анонім"  # Ім'я користувача за замовчуванням

        try:
            self.sock = socket(AF_INET,SOCK_STREAM)
            self.sock.connect(('152.53.83.62', 8080))
            self.send_text(f"[SYSTEM] {self.username} приєднався(лась) до чату!")
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")
            self.sock = None

        # Налаштовуємо сітку головного вікна: 3 колонки, 1 рядок
        self.grid_columnconfigure(2, weight=1)  # Колонка з чатом буде розтягуватися
        self.grid_rowconfigure(0, weight=1)  # Єдиний рядок теж розтягуваний

        # ==== Бокове меню (Sidebar) ====
        # Створюємо фрейм зліва для введення імені
        self.sidebar_frame = CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")  # Прив'язуємо до лівого краю
        self.sidebar_frame.grid_propagate(False)  # Забороняємо автоматичне змінення розміру
        self.sidebar_frame.grid_remove()  # Початково ховаємо панель

        # Мітка для поля імені
        self.sidebar_label = CTkLabel(self.sidebar_frame, text="Ваш нікнейм:", anchor="w")
        self.sidebar_label.pack(padx=20, pady=(20, 5), anchor="w")

        # Поле введення імені користувача
        self.name_entry = CTkEntry(self.sidebar_frame)
        self.name_entry.pack(padx=20, fill="x")

        # Кнопка збереження імені (ще не реалізована)
        self.save_button = CTkButton(self.sidebar_frame, text="Зберегти", command=self.update_username)
        self.save_button.pack(padx=20, pady=10, anchor="w")

        # ==== Кнопка відкриття/закриття бокового меню ====
        self.toggle_button = CTkButton(self, text="☰", width=40,
                                           command=self.toggle_sidebar)  # Кнопка з іконкою
        self.toggle_button.grid(row=0, column=1, sticky="n", padx=5, pady=10)

        # ==== Основна частина чату ====
        self.chat_frame = CTkFrame(self)
        self.chat_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Налаштовуємо сітку всередині чату
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)

        # Вікно, де будуть з'являтися повідомлення
        self.chat_display = CTkTextbox(self.chat_frame, wrap="word", state="disabled")
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        for color in self.colors:
            self.chat_display.tag_config(color, foreground=color)

        self.clear_button = CTkButton(self.chat_frame, text="Очистити", command=self.clear_chat)
        self.clear_button.grid(row=2, column=0, sticky="e", padx=5, pady=5)

        # ==== Поле введення повідомлення + кнопка надсилання ====
        self.entry_frame = CTkFrame(self.chat_frame)
        self.entry_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.entry_frame.grid_columnconfigure(0, weight=1)

        # Поле, де користувач пише повідомлення
        self.message_entry = CTkEntry(self.entry_frame)
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5)
        self.message_entry.bind("<Return>", lambda event: None)  # Поки що Enter нічого не робить

        # Кнопка надсилання повідомлення (поки не працює)
        self.send_button = CTkButton(self.entry_frame, text="Надіслати", command=self.send_message)
        self.send_button.grid(row=0, column=1, pady=5)

    # Метод відкриває або ховає бокове меню (toggle функція)
    def toggle_sidebar(self):
        if self.sidebar_frame.winfo_ismapped():  # Якщо меню вже показано
            self.sidebar_frame.grid_remove()     # Ховаємо його
        else:
            self.sidebar_frame.grid()            # Інакше — показуємо

    def update_username(self):
        new_name = self.name_entry.get().strip()
        if new_name:
            self.username = new_name
            self.send_text(f"[SYSTEM] Ім'я змінено на: {self.username}")

    def add_message(self, text):
        random_color = random.choice(self.colors)
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text + "\n", random_color)
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def clear_chat(self):
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")

    def send_text(self, text):
        if self.sock:
            try:
                data = f"TEXT@{self.username}@{text}\n"
                self.sock.sendall(data.encode("utf-8"))
            except:
                self.add_message("Помилка відправки даних на сервер.")

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            self.send_text(message)
            self.add_message(f"{self.username}: {message}")
            self.message_entry.delete(0, "end")
            self.message_count += 1
            self.title(f"Chat ({self.message_count} повідомлень)")

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 2)
        if len(parts) >= 3 and parts[0] == "TEXT":
            author = parts[1]
            message = parts[2]
            self.add_message(f"{author}: {message}")
            if author != self.username:
                winsound.MessageBeep()
        else:
            self.add_message(line)


# Запуск застосунку
app = MainWindow()
app.mainloop()
