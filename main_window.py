import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from db_connect import get_all_products

def open_main_window(user):
    window = tk.Tk()
    window.title("Магазин обуви")
    window.geometry("1400x800")
    
    top_frame = tk.Frame(window, bg="#f0f0f0")
    top_frame.pack(fill=tk.X)
    
    user_name = user[1] if user[0] != 0 else "Гость"
    tk.Label(top_frame, text=f"Пользователь: {user_name}", 
             font=("Arial", 10), bg="#f0f0f0").pack(side=tk.RIGHT, padx=10, pady=5)
    
    def logout():
        window.destroy()
        from auth_window import AuthWindow
        AuthWindow()
    
    tk.Button(top_frame, text="Выход", command=logout).pack(side=tk.LEFT, padx=10, pady=5)
    
    canvas_frame = tk.Frame(window)
    canvas_frame.pack(fill=tk.BOTH, expand=True)
    
    canvas = tk.Canvas(canvas_frame)
    scroll_y = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scroll_x = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    
    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    
    headers = ["Фото", "Артикул", "Наименование", "Категория", "Описание", 
               "Производитель", "Поставщик", "Цена", "Ед. изм.", "Кол-во", "Скидка %"]
    
    for col, header in enumerate(headers):
        lbl = tk.Label(inner_frame, text=header, font=("Arial", 10, "bold"),
                       borderwidth=1, relief="solid", padx=5, pady=5, bg="#d9d9d9")
        lbl.grid(row=0, column=col, sticky="nsew")
    
    products = get_all_products()
    
    def load_image(photo_name):
        image_path = None
        if photo_name:
            possible_paths = [
                f"images/{photo_name}",
                f"./images/{photo_name}",
                f"images/{photo_name}.jpg",
                f"../images/{photo_name}"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    image_path = path
                    break
        
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Ошибка загрузки {image_path}: {e}")
        
        img = Image.new('RGB', (60, 60), color='#cccccc')
        return ImageTk.PhotoImage(img)
    
    photo_images = {}
    
    for row_idx, p in enumerate(products, start=1):
        (article, name, category, desc, manufacturer, supplier, 
         price, unit, stock, discount, photo) = p
        
        final_price = price * (100 - discount) / 100
        
        row_bg = None
        if stock == 0:
            row_bg = "#ADD8E6"  
        elif discount > 15:
            row_bg = "#2E8B57"  
        
        img = load_image(photo)
        photo_images[f"row_{row_idx}"] = img
        lbl_photo = tk.Label(inner_frame, image=img, borderwidth=1, relief="solid")
        lbl_photo.grid(row=row_idx, column=0, sticky="nsew", padx=0, pady=0)
        if row_bg:
            lbl_photo.configure(bg=row_bg)
        
        lbl_article = tk.Label(inner_frame, text=article, borderwidth=1, relief="solid", padx=5, pady=5)
        lbl_article.grid(row=row_idx, column=1, sticky="nsew")
        
        lbl_name = tk.Label(inner_frame, text=name, borderwidth=1, relief="solid", padx=5, pady=5)
        lbl_name.grid(row=row_idx, column=2, sticky="nsew")
        
        lbl_category = tk.Label(inner_frame, text=category, borderwidth=1, relief="solid", padx=5, pady=5)
        lbl_category.grid(row=row_idx, column=3, sticky="nsew")
        
        lbl_desc = tk.Label(inner_frame, text=(desc or "")[:50], borderwidth=1, relief="solid", padx=5, pady=5)
        lbl_desc.grid(row=row_idx, column=4, sticky="nsew")
        
        lbl_manufacturer = tk.Label(inner_frame, text=manufacturer, borderwidth=1, relief="solid", padx=5, pady=5)
        lbl_manufacturer.grid(row=row_idx, column=5, sticky="nsew")
        
        lbl_supplier = tk.Label(inner_frame, text=supplier, borderwidth=1, relief="solid", padx=5, pady=5)
        lbl_supplier.grid(row=row_idx, column=6, sticky="nsew")
        
        if discount > 0:
            price_text = f"₽{price:.0f}  ₽{final_price:.0f}"
            lbl_price = tk.Label(inner_frame, text=price_text, borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_price.grid(row=row_idx, column=7, sticky="nsew")
            pass
        else:
            lbl_price = tk.Label(inner_frame, text=f"₽{price:.0f}", borderwidth=1, relief="solid", padx=5, pady=5)
            lbl_price.grid(row=row_idx, column=7, sticky="nsew")
        
        lbl_unit = tk.Label(inner_frame, text=unit, borderwidth=1, relief="solid", padx=5, pady=5)
        lbl_unit.grid(row=row_idx, column=8, sticky="nsew")
        
        lbl_stock = tk.Label(inner_frame, text=stock, borderwidth=1, relief="solid", padx=5, pady=5)
        lbl_stock.grid(row=row_idx, column=9, sticky="nsew")
        
        lbl_discount = tk.Label(inner_frame, text=f"{discount}%", borderwidth=1, relief="solid", padx=5, pady=5)
        lbl_discount.grid(row=row_idx, column=10, sticky="nsew")
        
        if row_bg:
            for widget in [lbl_photo, lbl_article, lbl_name, lbl_category, lbl_desc,
                          lbl_manufacturer, lbl_supplier, lbl_price, lbl_unit, lbl_stock, lbl_discount]:
                widget.configure(bg=row_bg)
        
        if discount > 0:
            lbl_price.destroy()
            
            price_frame = tk.Frame(inner_frame, borderwidth=1, relief="solid")
            price_frame.grid(row=row_idx, column=7, sticky="nsew")
            
            old_price = tk.Label(price_frame, text=f"₽{price:.0f}", fg="red", font=("Arial", 9, "overstrike"))
            old_price.pack(side="left", padx=2)
            
            new_price = tk.Label(price_frame, text=f"₽{final_price:.0f}", fg="black", font=("Arial", 9, "bold"))
            new_price.pack(side="left", padx=2)
            
            if row_bg:
                price_frame.configure(bg=row_bg)
                old_price.configure(bg=row_bg)
                new_price.configure(bg=row_bg)
    
    for col in range(len(headers)):
        inner_frame.grid_columnconfigure(col, weight=1)
    
    inner_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_shift_mousewheel(event):
        canvas.xview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind("<MouseWheel>", on_mousewheel)
    canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel)
    
    window.mainloop()