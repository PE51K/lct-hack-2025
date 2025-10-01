-- PostgreSQL test data initialization

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    department VARCHAR(50)
);

-- Insert test data
INSERT INTO employees (name, age, department) VALUES
('John Doe', 28, 'Engineering'),
('Jane Smith', 32, 'Marketing'),
('Alice Johnson', 29, 'HR'),
('Bob Wilson', 35, 'Finance'),
('Charlie Brown', 41, 'IT'),
('Diana Prince', 33, 'Legal');

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    category VARCHAR(50)
);

-- Insert test data
INSERT INTO products (name, price, category) VALUES
('Laptop', 1200.00, 'Electronics'),
('Book', 25.00, 'Education'),
('Phone', 800.00, 'Electronics'),
('Tablet', 500.00, 'Electronics'),
('Chair', 150.00, 'Furniture'),
('Notebook', 5.00, 'Stationery'),
('Monitor', 300.00, 'Electronics'),
('Desk', 400.00, 'Furniture'),
('Pen', 2.00, 'Stationery');

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    amount DECIMAL(10,2),
    status VARCHAR(20)
);

-- Insert test data
INSERT INTO orders (id, amount, status) VALUES
(1001, 150.50, 'pending'),
(1002, 75.00, 'completed'),
(1003, 200.00, 'shipped'),
(1004, 50.25, 'pending'),
(1005, 300.75, 'completed'),
(1006, 125.00, 'cancelled');