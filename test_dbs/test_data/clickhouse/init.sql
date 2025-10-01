-- ClickHouse test data initialization

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id UInt32,
    name String,
    age UInt8,
    department String
) ENGINE = MergeTree()
ORDER BY id;

-- Insert test data
INSERT INTO employees VALUES
(1, 'John Doe', 28, 'Engineering'),
(2, 'Jane Smith', 32, 'Marketing'),
(3, 'Alice Johnson', 29, 'HR'),
(4, 'Bob Wilson', 35, 'Finance'),
(5, 'Charlie Brown', 41, 'IT'),
(6, 'Diana Prince', 33, 'Legal');

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id UInt32,
    name String,
    price Float32,
    category String
) ENGINE = MergeTree()
ORDER BY id;

-- Insert test data
INSERT INTO products VALUES
(1, 'Laptop', 1200.00, 'Electronics'),
(2, 'Book', 25.00, 'Education'),
(3, 'Phone', 800.00, 'Electronics'),
(4, 'Tablet', 500.00, 'Electronics'),
(5, 'Chair', 150.00, 'Furniture'),
(6, 'Notebook', 5.00, 'Stationery'),
(7, 'Monitor', 300.00, 'Electronics'),
(8, 'Desk', 400.00, 'Furniture'),
(9, 'Pen', 2.00, 'Stationery');

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id UInt32,
    amount Float32,
    status String
) ENGINE = MergeTree()
ORDER BY id;

-- Insert test data
INSERT INTO orders VALUES
(1001, 150.50, 'pending'),
(1002, 75.00, 'completed'),
(1003, 200.00, 'shipped'),
(1004, 50.25, 'pending'),
(1005, 300.75, 'completed'),
(1006, 125.00, 'cancelled');