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