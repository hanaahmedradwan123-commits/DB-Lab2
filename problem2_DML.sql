USE library;

-- 1. AUTHORS (5 authors: 2 from UK, Author 5 has 0 books)
INSERT INTO AUTHOR (name, country) VALUES
('Naguib Mahfouz', 'Egypt'),
('Agatha Christie', 'UK'),
('George Orwell', 'UK'),
('Taha Hussein', 'Egypt'),
('Haruki Murakami', 'Japan');

-- 2. PUBLISHERS (3 publishers: UK matches Agatha Christie & George Orwell)
INSERT INTO PUBLISHER (name, country) VALUES
('Dar El Shorouk', 'Egypt'),
('Penguin Books', 'UK'),
('HarperCollins', 'USA');

-- 3. CATEGORIES (3 categories)
INSERT INTO CATEGORY (name) VALUES
('Fiction'),
('Mystery'),
('Sci-Fi & Dystopia');

-- 4. BOOKS (10 books: Book 10 is never borrowed; several priced 15-20)
INSERT INTO BOOK (title, price, publish_year, author_id, publisher_id, category_id) VALUES
('Palace Walk', 18.50, 1956, 1, 1, 1),
('Sugar Street', 16.00, 1957, 1, 1, 1),
('Children of Gebelawi', 19.99, 1959, 1, 1, 1),
('Murder on the Orient Express', 15.50, 1934, 2, 2, 2),
('And Then There Were None', 14.00, 1939, 2, 2, 2),
('The Murder of Roger Ackroyd', 17.25, 1926, 2, 3, 2),
('1984', 16.99, 1949, 3, 2, 3),
('Animal Farm', 11.50, 1945, 3, 2, 3),
('The Days', 13.00, 1929, 4, 1, 1),
('The Beggar', 22.00, 1965, 1, 3, 1);

-- 5. MEMBERS (5 members: Member 5 has 0 loans)
INSERT INTO MEMBER (name, email, join_date) VALUES
('Hana Ahmed', 'hana@example.com', '2026-01-10'),
('Omar Khaled', 'omar@example.com', '2026-02-14'),
('Salma Mahmoud', 'salma@example.com', '2026-03-05'),
('Ali Hassan', 'ali@example.com', '2026-04-20'),
('Youssef Tarek', 'youssef@example.com', '2026-05-12');

-- 6. LOANS (12 loans: Book 10 never borrowed; Member 5 has 0 loans; 3 active NULL returns)
INSERT INTO LOAN (book_id, member_id, loan_date, return_date) VALUES
(1, 1, '2026-06-01', '2026-06-15'),
(1, 2, '2026-07-01', '2026-07-14'),
(1, 3, '2026-08-05', '2026-08-19'),
(1, 4, '2026-11-01', NULL),
(4, 1, '2026-06-10', '2026-06-24'),
(4, 2, '2026-09-01', '2026-09-15'),
(4, 3, '2026-11-05', NULL),
(7, 1, '2026-07-12', '2026-07-26'),
(7, 4, '2026-10-01', '2026-10-15'),
(2, 1, '2026-08-15', '2026-08-29'),
(5, 2, '2026-09-20', '2026-10-04'),
(8, 3, '2026-11-08', NULL);