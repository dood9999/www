import sqlite3
import buildozer 
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY,
                                username TEXT,
                                password TEXT,
                                score INTEGER DEFAULT 0
                                )''')
            self.conn.commit()
        except Exception as e:
            print("Error creating table:", e)

    def register_user(self, username, password):
        self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()

    def login_user(self, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return self.cursor.fetchone()

    def update_score(self, username, score):
        self.cursor.execute("UPDATE users SET score=? WHERE username=?", (score, username))
        self.conn.commit()


class AddScorePopup(Popup):
    def __init__(self, username, on_confirm, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Введите пароль, чтобы добавить счет'
        self.size_hint = (None, None)
        self.size = (400, 300)  # Increased size
        self.username = username

        self.password_input = TextInput(hint_text="Enter password", multiline=False, password=True)
        self.btn_confirm = Button(text="Confirm", size_hint=(None, None), size=(150, 50))
        self.btn_confirm.bind(on_press=self.confirm_password)

        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(self.password_input)
        layout.add_widget(self.btn_confirm)

        self.add_widget(layout)

        self.on_confirm = on_confirm

    def confirm_password(self, instance):
        password = self.password_input.text
        if password == "admin890admin123321":
            self.on_confirm()
            self.dismiss()
        else:
            self.password_input.text = ""
            self.password_input.hint_text = "Неверный пароль!"


class MenuScreen(BoxLayout):
    def __init__(self, username, score, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.username = username
        self.score = score
        self.db_manager = db_manager

        self.label = Label(text=f"Hello, {self.username}!\nSCORE: {self.score}", size_hint=(1, 0.5))
        self.add_widget(self.label)

        self.btn_add_score = Button(text="Add Score", size_hint=(1, 0.1))
        self.btn_add_score.bind(on_press=self.open_add_score_popup)
        self.add_widget(self.btn_add_score)

    def update_label(self):
        self.label.text = f"Hello, {self.username}!\nSCORE: {self.score}"

    def open_add_score_popup(self, instance):
        pop = AddScorePopup(self.username, on_confirm=self.add_score)
        pop.open()

    def add_score(self):
        self.score += 1
        self.update_score_in_db()
        self.update_label()

    def update_score_in_db(self):
        self.db_manager.update_score(self.username, self.score)


class MyApp(App):
    def build(self):
        db_manager = DatabaseManager()
        return LoginScreen(db_manager)


class LoginScreen(BoxLayout):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.db_manager = db_manager

        self.label = Label(text="Добро пожаловать!", size_hint=(1, 0.5))
        self.add_widget(self.label)

        self.username_input = TextInput(hint_text="Введите имя пользователя", multiline=False, size_hint=(1, 0.1))
        self.add_widget(self.username_input)

        self.password_input = TextInput(hint_text="Введите пароль", multiline=False, password=True, size_hint=(1, 0.1))
        self.add_widget(self.password_input)

        self.btn_register = Button(text="регистрация", size_hint=(1, 0.1))
        self.btn_register.bind(on_press=self.register)
        self.add_widget(self.btn_register)

        self.btn_login = Button(text="вход", size_hint=(1, 0.1))
        self.btn_login.bind(on_press=self.login)
        self.add_widget(self.btn_login)

    def register(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        existing_user = self.db_manager.login_user(username, password)
        if existing_user:
            self.label.text = "Пользователь уже существует!"
        else:
            self.db_manager.register_user(username, password)
            self.label.text = "Пользователь зарегистрирован!"

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        user = self.db_manager.login_user(username, password)
        if user:
            self.label.text = "Login successful!"
            score = user[3] if len(user) > 3 else 0
            self.parent.add_widget(MenuScreen(username=username, score=score, db_manager=self.db_manager))
            self.parent.remove_widget(self)
        else:
            self.label.text = "Неверное имя пользователя или пароль!"


if __name__ == '__main__':
    MyApp().run()
