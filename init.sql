-- Database initialization script for Goline Library Chatbot
-- Create tables and insert sample data

-- Create books table
CREATE TABLE IF NOT EXISTS books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(500) NOT NULL,
    book_id INTEGER REFERENCES books(book_id),
    quantity INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert 20 mock books
INSERT INTO books (title, author, price, stock, category) VALUES
('Tôi Thấy Hoa Vàng Trên Cỏ Xanh', 'Nguyễn Nhật Ánh', 85000, 50, 'Văn học'),
('Số Đỏ', 'Vũ Trọng Phụng', 120000, 30, 'Văn học'),
('Dế Mèn Phiêu Lưu Ký', 'Tô Hoài', 65000, 40, 'Thiếu nhi'),
('Lão Hạc', 'Nam Cao', 75000, 35, 'Văn học'),
('Chí Phèo', 'Nam Cao', 70000, 25, 'Văn học'),
('Tắt Đèn', 'Ngô Tất Tố', 90000, 20, 'Văn học'),
('Sapiens: Lược Sử Loài Người', 'Yuval Noah Harari', 250000, 45, 'Lịch sử'),
('Nhà Giả Kim', 'Paulo Coelho', 180000, 60, 'Tiểu thuyết'),
('Đắc Nhân Tâm', 'Dale Carnegie', 150000, 80, 'Kỹ năng sống'),
('Atomic Habits', 'James Clear', 220000, 55, 'Kỹ năng sống'),
('The 7 Habits of Highly Effective People', 'Stephen Covey', 195000, 40, 'Kỹ năng sống'),
('Clean Code', 'Robert C. Martin', 350000, 25, 'Công nghệ'),
('Python Crash Course', 'Eric Matthes', 420000, 30, 'Công nghệ'),
('Design Patterns', 'Gang of Four', 380000, 20, 'Công nghệ'),
('Algorithms', 'Robert Sedgewick', 450000, 15, 'Công nghệ'),
('Hoàng Tử Bé', 'Antoine de Saint-Exupéry', 95000, 70, 'Thiếu nhi'),
('Harry Potter và Hòn Đá Phù Thủy', 'J.K. Rowling', 280000, 65, 'Giả tưởng'),
('1984', 'George Orwell', 165000, 35, 'Tiểu thuyết'),
('To Kill a Mockingbird', 'Harper Lee', 175000, 30, 'Tiểu thuyết'),
('The Great Gatsby', 'F. Scott Fitzgerald', 155000, 40, 'Tiểu thuyết');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_name);

-- Display inserted data
SELECT 'Books inserted successfully' as message;
SELECT COUNT(*) as total_books FROM books;
