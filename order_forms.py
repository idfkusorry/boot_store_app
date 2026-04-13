import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db_connect import *

class OrderForm:
    def __init__(self, parent, refresh_callback, user_role, order_id=None):
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.user_role = user_role
        self.order_id = order_id
        self.order_items = []  
        
        self.window = tk.Toplevel(parent)
        if order_id:
            self.window.title(f"Редактирование заказа №{order_id}")
        else:
            self.window.title("Добавление заказа")
        self.window.geometry("750x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        if order_id:
            self.load_order_data()
            self.load_order_items()
    
    def create_widgets(self):
        # Фрейм для основной информации
        main_frame = tk.LabelFrame(self.window, text="Информация о заказе", padx=10, pady=10)
        main_frame.pack(fill=tk.X, padx=10, pady=10)
        
        row = 0
        
        tk.Label(main_frame, text="ID заказа:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.id_entry = tk.Entry(main_frame, width=30)
        self.id_entry.grid(row=row, column=1, padx=5, pady=5)
        if self.order_id:
            self.id_entry.insert(0, self.order_id)
            self.id_entry.config(state="readonly")
        row += 1
        
        tk.Label(main_frame, text="Статус заказа:*").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.status_combo = ttk.Combobox(main_frame, width=27)
        self.status_combo.grid(row=row, column=1, padx=5, pady=5)
        statuses = get_all_statuses()
        self.status_values = {name: id_status for id_status, name in statuses}
        self.status_combo['values'] = list(self.status_values.keys())
        row += 1
        
        tk.Label(main_frame, text="Пункт выдачи:*").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.pickup_combo = ttk.Combobox(main_frame, width=27)
        self.pickup_combo.grid(row=row, column=1, padx=5, pady=5)
        points = get_all_pickup_points()
        self.pickup_values = {address: id_point for id_point, address in points}
        self.pickup_combo['values'] = list(self.pickup_values.keys())
        row += 1
        
        tk.Label(main_frame, text="Клиент:*").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.client_combo = ttk.Combobox(main_frame, width=27)
        self.client_combo.grid(row=row, column=1, padx=5, pady=5)
        clients = get_all_users_by_role()
        self.client_values = {name: id_user for id_user, name in clients}
        self.client_combo['values'] = list(self.client_values.keys())
        row += 1
        
        tk.Label(main_frame, text="Код получения:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.code_entry = tk.Entry(main_frame, width=32)
        self.code_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        tk.Label(main_frame, text="Дата заказа (ГГГГ-ММ-ДД):").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.order_date_entry = tk.Entry(main_frame, width=32)
        self.order_date_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        tk.Label(main_frame, text="Дата доставки (ГГГГ-ММ-ДД):").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.delivery_date_entry = tk.Entry(main_frame, width=32)
        self.delivery_date_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        items_frame = tk.LabelFrame(self.window, text="Товары в заказе", padx=10, pady=10)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Артикул", "Наименование", "Цена", "Количество", "Сумма")
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.items_tree.heading(col, text=col)
            self.items_tree.column(col, width=120)
        
        self.items_tree.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(items_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="+ Добавить товар", command=self.add_product_to_order,
                 bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="- Удалить товар", command=self.remove_product_from_order,
                 bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)
        
        save_frame = tk.Frame(self.window)
        save_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(save_frame, text="Сохранить заказ", command=self.save,
                 bg="#4CAF50", fg="white", padx=30, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=20)
        tk.Button(save_frame, text="Отмена", command=self.window.destroy,
                 bg="#f44336", fg="white", padx=30).pack(side=tk.LEFT, padx=20)
    
    def load_order_data(self):
        order = get_order_by_id(self.order_id)
        if order:
            (_, order_date, delivery_date, id_pickup_point, address,
             id_user, client_name, pickup_code, id_status, status_name) = order
            
            self.status_combo.set(status_name)
            self.pickup_combo.set(address)
            self.client_combo.set(client_name)
            self.code_entry.insert(0, pickup_code or "")
            self.order_date_entry.insert(0, order_date.strftime("%Y-%m-%d") if order_date else "")
            self.delivery_date_entry.insert(0, delivery_date.strftime("%Y-%m-%d") if delivery_date else "")
    
    def load_order_items(self):
        """Загрузка товаров в заказе"""
        self.order_items = get_order_items(self.order_id)
        self.refresh_items_table()
    
    def refresh_items_table(self):
        """Обновление таблицы товаров"""
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        total = 0
        for item in self.order_items:
            product = get_product_by_article(item[1])
            price = product[4] if product else 0
            amount = price * item[3]
            total += amount
            
            self.items_tree.insert("", tk.END, values=(
                item[1],  
                item[2],  
                f"{price:.2f}₽",
                item[3],  
                f"{amount:.2f}₽"
            ))
        
        # Показываем итого
        if hasattr(self, 'total_label'):
            self.total_label.destroy()
        self.total_label = tk.Label(self.items_tree.master, text=f"Итого: {total:.2f}₽", 
                                     font=("Arial", 10, "bold"), fg="blue")
        self.total_label.pack(anchor="e", pady=5)
    
    def add_product_to_order(self):
        """Диалог добавления товара в заказ"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Добавить товар")
        dialog.geometry("400x250")
        dialog.transient(self.window)
        dialog.grab_set()
        
        tk.Label(dialog, text="Выберите товар:").pack(pady=10)
        
        products = get_all_products()
        product_list = [(p[0], p[1]) for p in products]  
        product_names = [f"{p[0]} - {p[1]}" for p in product_list]
        
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(dialog, textvariable=product_var, width=40)
        product_combo['values'] = product_names
        product_combo.pack(pady=5)
        
        tk.Label(dialog, text="Количество:").pack(pady=5)
        quantity_entry = tk.Entry(dialog, width=10)
        quantity_entry.insert(0, "1")
        quantity_entry.pack()
        
        def add():
            if not product_var.get():
                messagebox.showerror("Ошибка", "Выберите товар")
                return
            
            try:
                quantity = int(quantity_entry.get())
                if quantity <= 0:
                    messagebox.showerror("Ошибка", "Количество должно быть больше 0")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Введите целое число")
                return
            
            selected = product_var.get()
            article = selected.split(" - ")[0]
            product_name = selected.split(" - ")[1]
            
            for item in self.order_items:
                if item[1] == article:
                    messagebox.showerror("Ошибка", "Этот товар уже добавлен в заказ")
                    return
            
            self.order_items.append((None, article, product_name, quantity))
            self.refresh_items_table()
            dialog.destroy()
        
        tk.Button(dialog, text="Добавить", command=add, bg="#4CAF50", fg="white").pack(pady=20)
    
    def remove_product_from_order(self):
        """Удаление товара из заказа"""
        selected = self.items_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return
        
        index = self.items_tree.index(selected[0])
        del self.order_items[index]
        self.refresh_items_table()
    
    def save_order_items(self, order_id):
        """Сохранение товаров заказа"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM order_item WHERE id_order = %s", (order_id,))
        
        for item in self.order_items:
            cur.execute("""
                INSERT INTO order_item (id_order, product_article, quantity)
                VALUES (%s, %s, %s)
            """, (order_id, item[1], item[3]))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def save(self):
        try:
            status_name = self.status_combo.get()
            if not status_name:
                messagebox.showerror("Ошибка", "Выберите статус")
                return
            
            address = self.pickup_combo.get()
            if not address:
                messagebox.showerror("Ошибка", "Выберите пункт выдачи")
                return
            
            client_name = self.client_combo.get()
            if not client_name:
                messagebox.showerror("Ошибка", "Выберите клиента")
                return
            
            if not self.order_items and not self.order_id:
                messagebox.showerror("Ошибка", "Добавьте хотя бы один товар в заказ")
                return
            
            pickup_code = self.code_entry.get()
            
            order_date = None
            if self.order_date_entry.get():
                order_date = datetime.strptime(self.order_date_entry.get(), "%Y-%m-%d").date()
            
            delivery_date = None
            if self.delivery_date_entry.get():
                delivery_date = datetime.strptime(self.delivery_date_entry.get(), "%Y-%m-%d").date()
            
            id_status = self.status_values[status_name]
            id_pickup_point = self.pickup_values[address]
            id_user = self.client_values[client_name]
            
            if self.order_id:
                update_order(self.order_id, order_date, delivery_date, 
                            id_pickup_point, id_user, pickup_code, id_status)
                self.save_order_items(self.order_id)
                messagebox.showinfo("Успех", "Заказ обновлен")
            else:
                new_id = add_order(order_date, delivery_date, id_pickup_point, 
                                  id_user, pickup_code, id_status)
                self.save_order_items(new_id)
                messagebox.showinfo("Успех", f"Заказ №{new_id} добавлен")
            
            self.window.destroy()
            self.refresh_callback()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат даты. Используйте ГГГГ-ММ-ДД\n{e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")