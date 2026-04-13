import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import *
from order_forms import OrderForm

class OrdersWindow:
    def __init__(self, parent, user_role):
        self.parent = parent
        self.user_role = user_role
        self.orders = []
        
        self.window = tk.Toplevel(parent)
        self.window.title("Управление заказами")
        self.window.geometry("1200x600")
        self.window.transient(parent)
        
        self.create_widgets()
        self.load_orders()
    
    def create_widgets(self):
        top_frame = tk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(top_frame, text="Список заказов", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        if self.user_role == "Администратор":
            btn_frame = tk.Frame(top_frame)
            btn_frame.pack(side=tk.RIGHT)
            tk.Button(btn_frame, text="+ Добавить заказ", command=self.add_order,
                     bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Обновить", command=self.load_orders).pack(side=tk.RIGHT, padx=5)
        tk.Button(top_frame, text="Назад", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
        table_frame = tk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        scroll_y = tk.Scrollbar(table_frame, orient="vertical")
        scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(table_frame, 
                                  columns=("ID", "Дата заказа", "Дата доставки", 
                                          "Пункт выдачи", "Клиент", "Код получения", "Статус"),
                                  show="headings",
                                  yscrollcommand=scroll_y.set,
                                  xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        self.tree.heading("ID", text="№ заказа")
        self.tree.heading("Дата заказа", text="Дата заказа")
        self.tree.heading("Дата доставки", text="Дата доставки")
        self.tree.heading("Пункт выдачи", text="Пункт выдачи")
        self.tree.heading("Клиент", text="Клиент")
        self.tree.heading("Код получения", text="Код получения")
        self.tree.heading("Статус", text="Статус")
        
        self.tree.column("ID", width=80)
        self.tree.column("Дата заказа", width=120)
        self.tree.column("Дата доставки", width=120)
        self.tree.column("Пункт выдачи", width=300)
        self.tree.column("Клиент", width=200)
        self.tree.column("Код получения", width=100)
        self.tree.column("Статус", width=120)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        if self.user_role == "Администратор":
            action_frame = tk.Frame(self.window)
            action_frame.pack(fill=tk.X, padx=10, pady=10)
            
            tk.Button(action_frame, text="Редактировать", command=self.edit_order,
                     bg="#2196F3", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
            tk.Button(action_frame, text="Удалить", command=self.delete_order,
                     bg="#f44336", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
            
            self.tree.bind("<Double-1>", lambda e: self.edit_order())
        
        tk.Label(self.window, text="Состав заказа:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        
        items_frame = tk.Frame(self.window)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.items_tree = ttk.Treeview(items_frame, columns=("Артикул", "Товар", "Количество"), show="headings", height=6)
        self.items_tree.heading("Артикул", text="Артикул")
        self.items_tree.heading("Товар", text="Товар")
        self.items_tree.heading("Количество", text="Количество")
        self.items_tree.column("Артикул", width=100)
        self.items_tree.column("Товар", width=300)
        self.items_tree.column("Количество", width=100)
        self.items_tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_order_select)
    
    def load_orders(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.orders = get_all_orders()
        for order in self.orders:
            self.tree.insert("", tk.END, values=(
                order[0],  # id
                order[1].strftime("%Y-%m-%d") if order[1] else "",
                order[2].strftime("%Y-%m-%d") if order[2] else "",
                order[3],  # address
                order[4],  # client
                order[5],  # pickup_code
                order[6]   # status
            ))
    
    def on_order_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        order_id = self.tree.item(selected[0])['values'][0]
        
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        items = get_order_items(order_id)
        for item in items:
            self.items_tree.insert("", tk.END, values=(item[1], item[2], item[3]))
    
    def add_order(self):
        OrderForm(self.window, self.load_orders, self.user_role)
    
    def edit_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ для редактирования")
            return
        
        order_id = self.tree.item(selected[0])['values'][0]
        OrderForm(self.window, self.load_orders, self.user_role, order_id)
    
    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ для удаления")
            return
        
        order_id = self.tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить заказ №{order_id}?"):
            try:
                delete_order(order_id)
                messagebox.showinfo("Успех", "Заказ удален")
                self.load_orders()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить заказ: {e}")