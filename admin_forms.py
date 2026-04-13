import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil
from db_connect import *

class ProductForm:
    def __init__(self, parent, refresh_callback, article=None):
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.article = article
        self.photo_path = None
        self.current_photo = None
        
        self.window = tk.Toplevel(parent)
        if article:
            self.window.title("Редактирование товара")
        else:
            self.window.title("Добавление товара")
        self.window.geometry("600x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        if article:
            self.load_product_data()
    
    def create_widgets(self):
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        row = 0
        
        tk.Label(scrollable_frame, text="Фото:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.photo_label = tk.Label(scrollable_frame, text="Нет фото", width=30, height=10, relief="solid")
        self.photo_label.grid(row=row, column=1, padx=5, pady=5)
        tk.Button(scrollable_frame, text="Выбрать фото", command=self.select_photo).grid(row=row, column=2, padx=5, pady=5)
        row += 1
        
        tk.Label(scrollable_frame, text="Артикул:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.article_entry = tk.Entry(scrollable_frame, width=30)
        self.article_entry.grid(row=row, column=1, padx=5, pady=5)
        if self.article:
            self.article_entry.insert(0, self.article)
            self.article_entry.config(state="readonly")
        row += 1
        
        tk.Label(scrollable_frame, text="Наименование:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.name_combo = ttk.Combobox(scrollable_frame, width=27)
        self.name_combo.grid(row=row, column=1, padx=5, pady=5)
        product_names = get_product_names()
        self.name_values = {name: id_name for id_name, name in product_names}
        self.name_combo['values'] = list(self.name_values.keys())
        row += 1
        
        tk.Label(scrollable_frame, text="Категория:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.category_combo = ttk.Combobox(scrollable_frame, width=27)
        self.category_combo.grid(row=row, column=1, padx=5, pady=5)
        categories = get_categories()
        self.category_values = {name: id_cat for id_cat, name in categories}
        self.category_combo['values'] = list(self.category_values.keys())
        row += 1
        
        tk.Label(scrollable_frame, text="Производитель:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.manufacturer_combo = ttk.Combobox(scrollable_frame, width=27)
        self.manufacturer_combo.grid(row=row, column=1, padx=5, pady=5)
        manufacturers = get_manufacturers()
        self.manufacturer_values = {name: id_man for id_man, name in manufacturers}
        self.manufacturer_combo['values'] = list(self.manufacturer_values.keys())
        row += 1
        
        tk.Label(scrollable_frame, text="Поставщик:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.supplier_combo = ttk.Combobox(scrollable_frame, width=27)
        self.supplier_combo.grid(row=row, column=1, padx=5, pady=5)
        suppliers = get_suppliers()
        self.supplier_values = {name: id_sup for id_sup, name in suppliers}
        self.supplier_combo['values'] = list(self.supplier_values.keys())
        row += 1
        
        tk.Label(scrollable_frame, text="Цена:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.price_entry = tk.Entry(scrollable_frame, width=30)
        self.price_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        tk.Label(scrollable_frame, text="Ед. измерения:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.unit_entry = tk.Entry(scrollable_frame, width=30)
        self.unit_entry.insert(0, "шт.")
        self.unit_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        tk.Label(scrollable_frame, text="Количество на складе:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.quantity_entry = tk.Entry(scrollable_frame, width=30)
        self.quantity_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        tk.Label(scrollable_frame, text="Скидка (%):").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.discount_entry = tk.Entry(scrollable_frame, width=30)
        self.discount_entry.insert(0, "0")
        self.discount_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        tk.Label(scrollable_frame, text="Описание:").grid(row=row, column=0, sticky="ne", padx=5, pady=5)
        self.description_text = tk.Text(scrollable_frame, width=30, height=5)
        self.description_text.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        btn_frame = tk.Frame(scrollable_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        tk.Button(btn_frame, text="Сохранить", command=self.save, bg="#4CAF50", fg="white", padx=20).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.window.destroy, bg="#f44336", fg="white", padx=20).pack(side="left", padx=10)
    
    def select_photo(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        filename = filedialog.askopenfilename(title="Выберите фото", filetypes=filetypes)
        if filename:
            self.photo_path = filename
            img = Image.open(filename)
            img.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=photo, text="")
            self.photo_label.image = photo
    
    def load_product_data(self):
        product = get_product_by_article(self.article)
        if product:
            (_, id_product_name, product_name, unit, price, id_supplier, supplier_name,
             id_manufacturer, manufacturer_name, id_category, category_name,
             discount, quantity, description, photo) = product
            
            self.name_combo.set(product_name)
            self.category_combo.set(category_name)
            self.manufacturer_combo.set(manufacturer_name)
            self.supplier_combo.set(supplier_name)
            self.price_entry.insert(0, str(price))
            self.unit_entry.delete(0, tk.END)
            self.unit_entry.insert(0, unit)
            self.quantity_entry.insert(0, str(quantity))
            self.discount_entry.delete(0, tk.END)
            self.discount_entry.insert(0, str(discount))
            self.description_text.insert("1.0", description or "")
            self.current_photo = photo
            
            if photo and os.path.exists(f"images/{photo}"):
                img = Image.open(f"images/{photo}")
                img.thumbnail((150, 150))
                photo_img = ImageTk.PhotoImage(img)
                self.photo_label.config(image=photo_img, text="")
                self.photo_label.image = photo_img
    
    def save_photo(self):
        if self.photo_path:
            img = Image.open(self.photo_path)
            img.thumbnail((300, 200))
            
            ext = os.path.splitext(self.photo_path)[1]
            new_filename = f"product_{self.article_entry.get()}{ext}"
            save_path = os.path.join("images", new_filename)
            
            if self.current_photo and os.path.exists(f"images/{self.current_photo}"):
                os.remove(f"images/{self.current_photo}")
            
            img.save(save_path)
            return new_filename
        return self.current_photo
    
    def save(self):
        # Валидация
        try:
            article = self.article_entry.get().strip()
            if not article and not self.article:
                messagebox.showerror("Ошибка", "Артикул обязателен")
                return
            
            product_name = self.name_combo.get()
            if not product_name:
                messagebox.showerror("Ошибка", "Выберите наименование")
                return
            
            category = self.category_combo.get()
            if not category:
                messagebox.showerror("Ошибка", "Выберите категорию")
                return
            
            manufacturer = self.manufacturer_combo.get()
            if not manufacturer:
                messagebox.showerror("Ошибка", "Выберите производителя")
                return
            
            supplier = self.supplier_combo.get()
            if not supplier:
                messagebox.showerror("Ошибка", "Выберите поставщика")
                return
            
            price = float(self.price_entry.get())
            if price < 0:
                messagebox.showerror("Ошибка", "Цена не может быть отрицательной")
                return
            
            quantity = int(self.quantity_entry.get())
            if quantity < 0:
                messagebox.showerror("Ошибка", "Количество не может быть отрицательным")
                return
            
            discount = int(self.discount_entry.get())
            if discount < 0 or discount > 100:
                messagebox.showerror("Ошибка", "Скидка должна быть от 0 до 100")
                return
            
            unit = self.unit_entry.get()
            description = self.description_text.get("1.0", tk.END).strip()
            
            photo_filename = self.save_photo()
            
            if self.article:  
                update_product(
                    article, self.name_values[product_name], unit, price,
                    self.supplier_values[supplier], self.manufacturer_values[manufacturer],
                    self.category_values[category], discount, quantity, description, photo_filename
                )
                messagebox.showinfo("Успех", "Товар обновлен")
            else:  
                add_product(
                    article, self.name_values[product_name], unit, price,
                    self.supplier_values[supplier], self.manufacturer_values[manufacturer],
                    self.category_values[category], discount, quantity, description, photo_filename
                )
                messagebox.showinfo("Успех", "Товар добавлен")
            
            self.window.destroy()
            self.refresh_callback()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")