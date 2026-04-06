import tkinter as tk
from tkinter import messagebox
from db_connect import get_user_by_login_password
from main_window import open_main_window

class AuthWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Авторизация - Магазин обуви")
        self.window.geometry("400x300")
        
        tk.Label(self.window, text="Логин:").pack()
        self.entry_login = tk.Entry(self.window, width=30)
        self.entry_login.pack()
        
        tk.Label(self.window, text="Пароль:").pack()
        self.entry_password = tk.Entry(self.window, width=30, show="*")
        self.entry_password.pack()
        
        tk.Button(self.window, text="Войти", command=self.login, width=20).pack(pady=10)
        tk.Button(self.window, text="Войти как Гость", command=self.guest_login, width=20).pack()
        
        self.window.mainloop()
    
    def login(self):
        login = self.entry_login.get()
        password = self.entry_password.get()
        
        user = get_user_by_login_password(login, password)
        if user:
            self.window.destroy()
            open_main_window(user)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
    
    def guest_login(self):
        self.window.destroy()
        guest_data = (0, "Гость", "", "Гость")
        open_main_window(guest_data)