-- Sample database setup for Postgres NL Agent
-- This script creates sample tables and data for testing

-- Create sample tables
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO customers (name, email, phone) VALUES
    ('John Doe', 'john.doe@example.com', '+1-555-0101'),
    ('Jane Smith', 'jane.smith@example.com', '+1-555-0102'),
    ('Bob Johnson', 'bob.johnson@example.com', '+1-555-0103'),
    ('Alice Brown', 'alice.brown@example.com', '+1-555-0104'),
    ('Charlie Wilson', 'charlie.wilson@example.com', '+1-555-0105');

INSERT INTO products (name, description, price, stock_quantity) VALUES
    ('Laptop', 'High-performance laptop', 999.99, 50),
    ('Mouse', 'Wireless optical mouse', 29.99, 100),
    ('Keyboard', 'Mechanical keyboard', 89.99, 75),
    ('Monitor', '24-inch LED monitor', 199.99, 30),
    ('Headphones', 'Noise-cancelling headphones', 149.99, 60);

INSERT INTO orders (customer_id, order_number, total_amount, status) VALUES
    (1, 'ORD-001', 1029.98, 'completed'),
    (2, 'ORD-002', 89.99, 'pending'),
    (3, 'ORD-003', 349.98, 'shipped'),
    (4, 'ORD-004', 199.99, 'completed'),
    (5, 'ORD-005', 149.99, 'pending');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 999.99),
    (1, 2, 1, 29.99),
    (2, 3, 1, 89.99),
    (3, 4, 1, 199.99),
    (3, 5, 1, 149.99),
    (4, 4, 1, 199.99),
    (5, 5, 1, 149.99);

-- Create indexes for better performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Create a view for order summaries
CREATE VIEW order_summary AS
SELECT 
    o.id,
    o.order_number,
    c.name as customer_name,
    o.total_amount,
    o.status,
    o.created_at,
    COUNT(oi.id) as item_count
FROM orders o
JOIN customers c ON o.customer_id = c.id
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.order_number, c.name, o.total_amount, o.status, o.created_at;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user; 