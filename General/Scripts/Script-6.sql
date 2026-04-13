create database boot_store;

CREATE TABLE "role" (
    id_role SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE "category" (
    id_category SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE "manufacturer" (
    id_manufacturer SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE "supplier" (
    id_supplier SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE "pickup_point" (
    id_pickup_point SERIAL PRIMARY KEY,
    address TEXT UNIQUE NOT NULL
);

CREATE TABLE "status" (
    id_status SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE "product_name" (
    id_product_name SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE "user" (
    id_user SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    login VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    id_role INTEGER NOT NULL REFERENCES "role"(id_role)
);

CREATE TABLE "product" (
    article VARCHAR(20) PRIMARY KEY,
    id_product_name INTEGER NOT NULL REFERENCES "product_name"(id_product_name),
    unit VARCHAR(10) DEFAULT 'шт.',
    price DECIMAL(10,2) NOT NULL,
    id_supplier INTEGER NOT NULL REFERENCES "supplier"(id_supplier),
    id_manufacturer INTEGER NOT NULL REFERENCES "manufacturer"(id_manufacturer),
    id_category INTEGER NOT NULL REFERENCES "category"(id_category),
    discount INTEGER DEFAULT 0,
    quantity_in_stock INTEGER NOT NULL,
    description TEXT,
    photo VARCHAR(100)
);

CREATE TABLE "order" (
    id_order SERIAL PRIMARY KEY,
    order_date DATE,
    delivery_date DATE,
    id_pickup_point INTEGER NOT NULL REFERENCES "pickup_point"(id_pickup_point),
    id_user INTEGER NOT NULL REFERENCES "user"(id_user),
    pickup_code VARCHAR(20),
    id_status INTEGER NOT NULL REFERENCES "status"(id_status)
);

CREATE TABLE "order_item" (
    id_order_item SERIAL PRIMARY KEY,
    id_order INTEGER NOT NULL REFERENCES "order"(id_order) ON DELETE CASCADE,
    product_article VARCHAR(20) NOT NULL REFERENCES "product"(article),
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);
