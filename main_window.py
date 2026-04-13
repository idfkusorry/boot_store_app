import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from db_connect import *
from admin_forms import ProductForm

class MainWindow:
    def __init__(self, user):
        self.user = user
        self.role = user[3] if user[0] != 0 else "Гость"
        self.current_sort = "none"
        self.current_supplier_filter = "all"
        self.current_search = ""
        self.products = []
        self.photo_images = {}
        
        self.window = tk.Tk()
        self.window.title("Магазин обуви")
        self.window.geometry("1400x800")
        
        self.create_top_bar()
        self.create_filter_bar()
        self.create_products_table()
        self.load_products()
        
        self.window.mainloop()
    
    def create_top_bar(self):
        top_frame = tk.Frame(self.window, bg="#f0f0f0")
        top_frame.pack(fill=tk.X)
        
        user_name = self.user[1] if self.user[0] != 0 else "Гость"
        tk.Label(top_frame, text=f"Пользователь: {user_name} (роль: {self.role})",
                 font=("Arial", 10), bg="#f0f0f0").pack(side=tk.RIGHT, padx=10, pady=5)
        
        def logout():
            self.window.destroy()
            from auth_window import AuthWindow
            AuthWindow()
        
        tk.Button(top_frame, text="Выход", command=logout).pack(side=tk.LEFT, padx=10, pady=5)
        
        if self.role in ["Менеджер", "Администратор"]:
            tk.Button(top_frame, text="Заказы", command=self.open_orders,
                      bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        
        # Кнопки для администратора
        if self.role == "Администратор":
            tk.Button(top_frame, text="+ Добавить товар", command=self.add_product,
                      bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
    
    def open_orders(self):
        from orders_window import OrdersWindow
        OrdersWindow(self.window, self.role)
    
    def create_filter_bar(self):
        filter_frame = tk.Frame(self.window, bg="#e0e0e0")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if self.role in ["Менеджер", "Администратор"]:
            tk.Label(filter_frame, text="Поиск:", bg="#e0e0e0").pack(side=tk.LEFT, padx=5)
            self.search_var = tk.StringVar()
            self.search_var.trace("w", lambda *args: self.apply_filters())
            self.search_entry = tk.Entry(filter_frame, textvariable=self.search_var, width=30)
            self.search_entry.pack(side=tk.LEFT, padx=5)
            
            tk.Label(filter_frame, text="Поставщик:", bg="#e0e0e0").pack(side=tk.LEFT, padx=(20,5))
            self.supplier_var = tk.StringVar(value="all")
            self.supplier_combo = ttk.Combobox(filter_frame, textvariable=self.supplier_var, width=25)
            suppliers = [("all", "Все поставщики")] + [(s[1], s[1]) for s in get_suppliers()]
            self.supplier_combo['values'] = [s[1] for s in suppliers]
            self.supplier_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
            self.supplier_combo.pack(side=tk.LEFT, padx=5)
            
            tk.Label(filter_frame, text="Сортировка по кол-ву:", bg="#e0e0e0").pack(side=tk.LEFT, padx=(20,5))
            self.sort_var = tk.StringVar(value="none")
            sort_frame = tk.Frame(filter_frame, bg="#e0e0e0")
            sort_frame.pack(side=tk.LEFT)
            tk.Radiobutton(sort_frame, text="Нет", variable=self.sort_var, value="none",
                          command=self.apply_filters, bg="#e0e0e0").pack(side=tk.LEFT)
            tk.Radiobutton(sort_frame, text="По возрастанию", variable=self.sort_var, value="asc",
                          command=self.apply_filters, bg="#e0e0e0").pack(side=tk.LEFT)
            tk.Radiobutton(sort_frame, text="По убыванию", variable=self.sort_var, value="desc",
                          command=self.apply_filters, bg="#e0e0e0").pack(side=tk.LEFT)
    
    def create_products_table(self):
        table_frame = tk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(table_frame)
        scroll_y = tk.Scrollbar(table_frame, orient="vertical", command=self.canvas.yview)
        scroll_x = tk.Scrollbar(table_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        headers = ["Фото", "Артикул", "Наименование", "Категория", "Описание",
                   "Производитель", "Поставщик", "Цена", "Ед. изм.", "Кол-во", "Скидка %"]
        
        if self.role == "Администратор":
            headers.append("Действия")
        
        for col, header in enumerate(headers):
            lbl = tk.Label(self.inner_frame, text=header, font=("Arial", 10, "bold"),
                           borderwidth=1, relief="solid", padx=5, pady=5, bg="#d9d9d9")
            lbl.grid(row=0, column=col, sticky="nsew")
        
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", on_mousewheel)
    
    def load_products(self):
        for widget in self.inner_frame.winfo_children():
            if int(widget.grid_info()['row']) > 0:
                widget.destroy()
        
        if self.role in ["Менеджер", "Администратор"]:
            supplier_name = self.supplier_var.get() if self.supplier_var.get() != "all" else None
            supplier_id = None
            if supplier_name:
                suppliers = get_suppliers()
                for id_sup, name in suppliers:
                    if name == supplier_name:
                        supplier_id = id_sup
                        break
            
            self.products = get_filtered_sorted_products(
                self.current_search, supplier_id, self.current_sort
            )
        else:
            self.products = get_all_products()
        
        def load_image(photo_name):
            if photo_name and os.path.exists(f"images/{photo_name}"):
                try:
                    img = Image.open(f"images/{photo_name}")
                    img = img.resize((50, 50), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
                except:
                    pass
            img = Image.new('RGB', (50, 50), color='#cccccc')
            return ImageTk.PhotoImage(img)
        
        for row_idx, p in enumerate(self.products, start=1):
            (article, name, category, desc, manufacturer, supplier,
             price, unit, stock, discount, photo) = p
            
            final_price = price * (100 - discount) / 100
            
            row_bg = None
            if stock == 0:
                row_bg = "#ADD8E6"
            elif discount > 15:
                row_bg = "#2E8B57"
            
            img = load_image(photo)
            self.photo_images[f"row_{row_idx}"] = img
            lbl_photo = tk.Label(self.inner_frame, image=img, borderwidth=1, relief="solid")
            lbl_photo.grid(row=row_idx, column=0, sticky="nsew")
            
            lbl_article = tk.Label(self.inner_frame, text=article, borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_article.grid(row=row_idx, column=1, sticky="nsew")
            
            lbl_name = tk.Label(self.inner_frame, text=name, borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_name.grid(row=row_idx, column=2, sticky="nsew")
            
            lbl_category = tk.Label(self.inner_frame, text=category, borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_category.grid(row=row_idx, column=3, sticky="nsew")
            
            lbl_desc = tk.Label(self.inner_frame, text=(desc or "")[:40], borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_desc.grid(row=row_idx, column=4, sticky="nsew")
            
            lbl_manufacturer = tk.Label(self.inner_frame, text=manufacturer, borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_manufacturer.grid(row=row_idx, column=5, sticky="nsew")
            
            lbl_supplier = tk.Label(self.inner_frame, text=supplier, borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_supplier.grid(row=row_idx, column=6, sticky="nsew")
            
            if discount > 0:
                price_frame = tk.Frame(self.inner_frame, borderwidth=1, relief="solid")
                price_frame.grid(row=row_idx, column=7, sticky="nsew")
                
                old_price = tk.Label(price_frame, text=f"{price:.0f}₽", fg="red", font=("Arial", 9, "overstrike"))
                old_price.pack(side="left", padx=2)
                
                new_price = tk.Label(price_frame, text=f"{final_price:.0f}₽", fg="black", font=("Arial", 9, "bold"))
                new_price.pack(side="left", padx=2)
                
                if row_bg:
                    price_frame.configure(bg=row_bg)
                    old_price.configure(bg=row_bg)
                    new_price.configure(bg=row_bg)
            else:
                lbl_price = tk.Label(self.inner_frame, text=f"{price:.0f}₽", borderwidth=1, relief="solid", padx=5, pady=5)
                lbl_price.grid(row=row_idx, column=7, sticky="nsew")
                if row_bg:
                    lbl_price.configure(bg=row_bg)
            
            lbl_unit = tk.Label(self.inner_frame, text=unit, borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_unit.grid(row=row_idx, column=8, sticky="nsew")
            
            lbl_stock = tk.Label(self.inner_frame, text=stock, borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_stock.grid(row=row_idx, column=9, sticky="nsew")
            
            lbl_discount = tk.Label(self.inner_frame, text=f"{discount}%", borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_discount.grid(row=row_idx, column=10, sticky="nsew")
            
            if row_bg:
                for widget in [lbl_photo, lbl_article, lbl_name, lbl_category, lbl_desc,
                              lbl_manufacturer, lbl_supplier, lbl_unit, lbl_stock, lbl_discount]:
                    widget.configure(bg=row_bg)
                if discount > 0:
                    for widget in [old_price, new_price]:
                        widget.configure(bg=row_bg)
            
            if self.role == "Администратор":
                btn_frame = tk.Frame(self.inner_frame, borderwidth=1, relief="solid")
                btn_frame.grid(row=row_idx, column=11, sticky="nsew")
                
                def make_edit_func(a=article):
                    return lambda: self.edit_product(a)
                def make_delete_func(a=article, n=name):
                    return lambda: self.delete_product(a, n)
                
                tk.Button(btn_frame, text="Ред.", command=make_edit_func(), width=3).pack(side="left", padx=2, pady=2)
                tk.Button(btn_frame, text="Удал.", command=make_delete_func(), width=3, bg="#f44336", fg="white").pack(side="left", padx=2, pady=2)
                
                if row_bg:
                    btn_frame.configure(bg=row_bg)
        
        for col in range(len(self.inner_frame.grid_slaves(row=0))):
            self.inner_frame.grid_columnconfigure(col, weight=1)
        
        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def apply_filters(self):
        if self.role in ["Менеджер", "Администратор"]:
            self.current_search = self.search_var.get()
            self.current_sort = self.sort_var.get()
        self.load_products()
    
    def add_product(self):
        ProductForm(self.window, self.load_products)
    
    def edit_product(self, article):
        ProductForm(self.window, self.load_products, article)
    
    def delete_product(self, article, name):
        if is_product_in_orders(article):
            messagebox.showerror("Ошибка", f"Товар '{name}' находится в заказе и не может быть удален")
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить товар '{name}'?"):
            product = get_product_by_article(article)
            if product and product[14] and os.path.exists(f"images/{product[14]}"):
                os.remove(f"images/{product[14]}")
            
            delete_product(article)
            messagebox.showinfo("Успех", "Товар удален")
            self.load_products()

def open_main_window(user):
    MainWindow(user)