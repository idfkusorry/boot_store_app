import psycopg2
from config import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_user_by_login_password(login, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id_user, u.full_name, u.login, r.name as role_name
        FROM "user" u
        JOIN "role" r ON u.id_role = r.id_role
        WHERE u.login = %s AND u.password = %s
    """, (login, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            p.article,
            pn.name as product_name,
            c.name as category_name,
            p.description,
            m.name as manufacturer_name,
            s.name as supplier_name,
            p.price,
            p.unit,
            p.quantity_in_stock,
            p.discount,
            p.photo
        FROM product p
        JOIN product_name pn ON p.id_product_name = pn.id_product_name
        JOIN category c ON p.id_category = c.id_category
        JOIN manufacturer m ON p.id_manufacturer = m.id_manufacturer
        JOIN supplier s ON p.id_supplier = s.id_supplier
        ORDER BY pn.name
    """)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return products

# === НОВЫЕ ФУНКЦИИ ДЛЯ МОДУЛЯ 3 ===

def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_category, name FROM category ORDER BY name")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_manufacturers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_manufacturer, name FROM manufacturer ORDER BY name")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_suppliers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_supplier, name FROM supplier ORDER BY name")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_product_names():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_product_name, name FROM product_name ORDER BY name")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_product_by_article(article):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            p.article,
            pn.id_product_name,
            pn.name,
            p.unit,
            p.price,
            p.id_supplier,
            s.name as supplier_name,
            p.id_manufacturer,
            m.name as manufacturer_name,
            p.id_category,
            c.name as category_name,
            p.discount,
            p.quantity_in_stock,
            p.description,
            p.photo
        FROM product p
        JOIN product_name pn ON p.id_product_name = pn.id_product_name
        JOIN supplier s ON p.id_supplier = s.id_supplier
        JOIN manufacturer m ON p.id_manufacturer = m.id_manufacturer
        JOIN category c ON p.id_category = c.id_category
        WHERE p.article = %s
    """, (article,))
    product = cur.fetchone()
    cur.close()
    conn.close()
    return product

def add_product(article, id_product_name, unit, price, id_supplier, id_manufacturer, 
                id_category, discount, quantity, description, photo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO product (article, id_product_name, unit, price, id_supplier, 
                             id_manufacturer, id_category, discount, quantity_in_stock, 
                             description, photo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (article, id_product_name, unit, price, id_supplier, id_manufacturer,
          id_category, discount, quantity, description, photo))
    conn.commit()
    cur.close()
    conn.close()

def update_product(article, id_product_name, unit, price, id_supplier, id_manufacturer,
                   id_category, discount, quantity, description, photo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE product SET 
            id_product_name = %s, unit = %s, price = %s, id_supplier = %s,
            id_manufacturer = %s, id_category = %s, discount = %s, 
            quantity_in_stock = %s, description = %s, photo = %s
        WHERE article = %s
    """, (id_product_name, unit, price, id_supplier, id_manufacturer,
          id_category, discount, quantity, description, photo, article))
    conn.commit()
    cur.close()
    conn.close()

def delete_product(article):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM product WHERE article = %s", (article,))
    conn.commit()
    cur.close()
    conn.close()

def is_product_in_orders(article):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM order_item WHERE product_article = %s", (article,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count > 0

def get_filtered_sorted_products(search_text, supplier_id, sort_order):
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            p.article,
            pn.name as product_name,
            c.name as category_name,
            p.description,
            m.name as manufacturer_name,
            s.name as supplier_name,
            p.price,
            p.unit,
            p.quantity_in_stock,
            p.discount,
            p.photo
        FROM product p
        JOIN product_name pn ON p.id_product_name = pn.id_product_name
        JOIN category c ON p.id_category = c.id_category
        JOIN manufacturer m ON p.id_manufacturer = m.id_manufacturer
        JOIN supplier s ON p.id_supplier = s.id_supplier
        WHERE 1=1
    """
    params = []
    
    # Поиск по тексту
    if search_text:
        query += """ AND (
            pn.name ILIKE %s OR 
            c.name ILIKE %s OR 
            p.description ILIKE %s OR 
            m.name ILIKE %s OR 
            s.name ILIKE %s OR
            p.article ILIKE %s
        )"""
        search_pattern = f"%{search_text}%"
        params.extend([search_pattern] * 6)
    
    # Фильтр по поставщику
    if supplier_id and supplier_id != "all":
        query += " AND p.id_supplier = %s"
        params.append(supplier_id)
    
    # Сортировка
    if sort_order == "asc":
        query += " ORDER BY p.quantity_in_stock ASC"
    elif sort_order == "desc":
        query += " ORDER BY p.quantity_in_stock DESC"
    else:
        query += " ORDER BY pn.name"
    
    cur.execute(query, params)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return products