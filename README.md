# Introduction to Database Systems — Lab 4
## Alexandria National University | Faculty of Engineering
### Fall 2026

**Student:** Bouthina Mohamed Abdelwahab
**Student ID:** 2304065

**Team Member:** Hana Ahmed Shehata
**Student ID:** 2304081

---

## Project Overview

This repository contains the database and web application deliverables for Lab 4, extending the work completed in Lab 3.

The project has two main parts:

- **Problem 1 — COMPANY Database:** Creating and populating the COMPANY database, demonstrating INSERT, UPDATE, DELETE, transactions, aggregate functions, filtering, grouping, INNER JOIN, LEFT JOIN, and self joins.
- **Problem 2 — Library Database and Website:** Implementing the library database with Authors, Publishers, Categories, Books, Members, and Loans, and extending the existing Flask website with search, catalogue, reports, loans, and author-related pages.

The existing Flask application also retains its Lab 3 features, including user registration, login, To-Do management, and Library CRUD operations.

---

## Repository Structure

```text
DB-Lab2/
│
├── problem1_DDL.sql
├── problem1_DML.sql
├── problem1_Answers.txt
│
├── problem2_DDL.sql
├── problem2_DML.sql
├── problem2_Queries.sql
│
├── README.md
│
├── database/
│   └── schema.sql
│
└── website/
    ├── app.py
    ├── .env.example
    ├── static/
    │   ├── style.css
    │   └── uploads/
    │
    └── templates/
        ├── library.html
        ├── add_author.html
        ├── edit_author.html
        ├── add_book.html
        ├── edit_book.html
        ├── authors_books.html
        ├── catalogue.html
        ├── search_books.html
        ├── reports.html
        ├── loans.html
        ├── most_borrowed.html
        ├── login.html
        ├── register.html
        ├── todos.html
        └── edit_todo.html
```

---

# Part I — Problem 1: COMPANY Database

## Database Schema

The COMPANY database contains five tables:

| Table | Description |
|---|---|
| EMPLOYEE | Employee details, salaries, supervisors, and departments |
| DEPARTMENT | Department details and managers |
| PROJECT | Company projects and their departments |
| WORKS_ON | Employees assigned to projects and their working hours |
| DEPENDENT | Employee dependents |

### Relationships and Foreign Keys

- `EMPLOYEE.Dno` references `DEPARTMENT.Dnumber`.
- `EMPLOYEE.super_ssn` references `EMPLOYEE.ssn`.
- `DEPARTMENT.mgr_ssn` references `EMPLOYEE.ssn`.
- `PROJECT.Dno` references `DEPARTMENT.Dnumber`.
- `WORKS_ON.essn` references `EMPLOYEE.ssn`.
- `WORKS_ON.Pno` references `PROJECT.Pnumber`.
- `DEPENDENT.essn` references `EMPLOYEE.ssn`.

The supervisor and department manager references may be NULL.

## SQL Scripts

- `problem1_DDL.sql`: Creates the COMPANY database and its five tables, including primary keys and foreign key constraints.
- `problem1_DML.sql`: Inserts sample departments, employees, projects, work assignments, and dependents.
- `problem1_Answers.txt`: Contains the SQL statements, execution outputs, errors, and explanations for Q1.1–Q1.12.

## Problem 1 Coverage

| Question | Topic | Implementation |
|---|---|---|
| Q1.1 | INSERT | Insert employee and project; test invalid department |
| Q1.2 | UPDATE | Salary increase, project location update, invalid department update |
| Q1.3 | DELETE | Delete dependent and work assignment, foreign key error, transaction and rollback |
| Q1.4 | WHERE, DISTINCT | Salary range, address filtering, NULL supervisor, distinct department numbers |
| Q1.5 | Aggregation | COUNT, SUM, AVG, MIN, MAX |
| Q1.6 | GROUP BY | Employee count and average salary per department |
| Q1.7 | HAVING | Departments with more than two employees |
| Q1.8 | INNER JOIN | Employee names and department names |
| Q1.9 | Multiple JOINs | Employee last names, project names, and hours |
| Q1.10 | LEFT JOIN | Departments with employee counts and projects without assignments |
| Q1.11 | Self JOIN | Employees and their supervisors |
| Q1.12 | JOIN, GROUP BY, HAVING | Total project hours, filtered and sorted |

---

# Part II — Problem 2: Library Database and Website

## Database Schema

The library database contains six main tables:

| Table | Description |
|---|---|
| AUTHOR | Author details and country |
| PUBLISHER | Publisher details and country |
| CATEGORY | Book categories |
| BOOK | Book details, price, year, author, publisher, and category |
| MEMBER | Library member information |
| LOAN | Book borrowing and return information |

### Relationships and Foreign Keys

- `BOOK.author_id` references `AUTHOR.author_id`.
- `BOOK.publisher_id` references `PUBLISHER.publisher_id`.
- `BOOK.category_id` references `CATEGORY.category_id`.
- `LOAN.book_id` references `BOOK.book_id`.
- `LOAN.member_id` references `MEMBER.member_id`.

The required cascading deletion behavior is implemented for authors and books. The `return_date` field is NULL when a book has not yet been returned.

The database also retains the existing `users` and `todos` tables used by the To-Do application.

## SQL Scripts

- `problem2_DDL.sql`: Creates the library database and its tables.
- `problem2_DML.sql`: Inserts sample authors, publishers, categories, books, members, and loans.
- `problem2_Queries.sql`: Contains the SQL queries used by the new website pages, organized with F2.1–F2.6 comments.

## Required Seed Data

The sample data is designed to cover the assignment requirements:

- At least four authors.
- At least three publishers.
- At least three categories.
- At least ten books.
- At least five members.
- At least twelve loans.
- Two authors from the same country.
- An author without books and an author with at least two books.
- An author and publisher from the same country.
- A book priced between 15 and 20.
- A book that has never been borrowed.
- A member who has never borrowed a book.
- At least one unreturned loan.

---

## Website Features

The existing Flask website has been extended with the following Lab 4 pages.

| Page | Route | Description |
|---|---|---|
| Search Books (F2.1) | `/search` | Search by title keyword, price range, and category |
| Catalogue (F2.2) | `/catalogue` | Display books with author, publisher, and category names |
| Reports (F2.3) | `/reports` | Category statistics, authors with at least two books, and library price statistics |
| Loans (F2.4) | `/loans` | Unreturned loans, members who never borrowed, and books never borrowed |
| Most Borrowed (F2.5) | `/most-borrowed` | Top three borrowed books and the member with the most loans |
| Authors and Books (F2.6) | `/authors-books` | All authors with book counts and books whose author and publisher share a country |

### Existing Lab 3 Features

The website also retains:

- User registration and login.
- Password hashing using bcrypt.
- Personal To-Do lists.
- Add, edit, and delete authors.
- Add, edit, and delete books.
- Author and book image uploads.
- Library management pages.

---

# How to Run the Project

## 1. Requirements

Install or configure:

- Python
- MySQL Server
- MySQL command-line client
- Flask
- PyMySQL
- python-dotenv
- bcrypt

## 2. Create the COMPANY Database

Open the MySQL client and run:

```sql
SOURCE C:/Users/Lenovo/DB-Lab2/problem1_DDL.sql;
SOURCE C:/Users/Lenovo/DB-Lab2/problem1_DML.sql;
```

To inspect the database:

```sql
USE company;
SHOW TABLES;
```

To run the assignment questions, use the SQL statements in `problem1_Answers.txt`.

## 3. Create the Library Database

Run the following scripts in the MySQL client:

```sql
SOURCE C:/Users/Lenovo/DB-Lab2/problem2_DDL.sql;
SOURCE C:/Users/Lenovo/DB-Lab2/problem2_DML.sql;
```

To inspect the tables:

```sql
USE library;
SHOW TABLES;
```

**Important:** The DDL scripts drop and recreate their respective databases. Running them again resets the corresponding database and its data.

## 4. Configure the Website

Open the `website` directory.

Create a local `.env` file based on `.env.example` and configure your own MySQL credentials:

```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=library
DB_PORT=3306
SECRET_KEY=your_secret_key
```

Use your own local database password and a private secret key. Do not commit your `.env` file to GitHub.

## 5. Install Python Dependencies

From the project directory, run:

```bash
cd website
pip install flask pymysql python-dotenv bcrypt
```

## 6. Start the Flask Application

From inside the `website` directory:

```bash
python app.py
```

Open the application in your browser:

- Library: http://127.0.0.1:5000/library
- To-Do list: http://127.0.0.1:5000/todos
- Search books: http://127.0.0.1:5000/search
- Catalogue: http://127.0.0.1:5000/catalogue
- Reports: http://127.0.0.1:5000/reports
- Loans: http://127.0.0.1:5000/loans
- Most borrowed: http://127.0.0.1:5000/most-borrowed
- Authors and books: http://127.0.0.1:5000/authors-books

---

## Technologies Used

- MySQL
- SQL
- Python
- Flask
- PyMySQL
- HTML
- CSS
- Jinja2
- bcrypt

---

## Submission

This repository contains the Lab 4 database scripts, answers, website implementation, and project documentation.

**Submission repository:**

https://github.com/hanaahmedradwan123-commits/DB-Lab2

**Course:** Introduction to Database Systems
**University:** Alexandria National University
**Faculty:** Faculty of Engineering
**Semester:** Fall 2026
