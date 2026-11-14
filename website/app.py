import os
import uuid
from pathlib import Path

import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
)
from werkzeug.utils import secure_filename


# ==================== CONFIGURATION ====================

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "AsAS1234@")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


# ==================== DATABASE CONNECTION ====================

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "AsAS1234@"),
        database=os.getenv("DB_NAME", "library"),
        port=int(os.getenv("DB_PORT", "3306")),
        cursorclass=pymysql.cursors.DictCursor,
    )


# ==================== IMAGE UPLOAD HELPERS ====================

def allowed_file(filename):
    return (
        bool(filename)
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_uploaded_image(file):
    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        raise ValueError("Invalid image format. Use PNG, JPG, JPEG, GIF, or WEBP.")

    original_name = secure_filename(file.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{extension}"

    destination = UPLOAD_FOLDER / new_filename
    file.save(destination)

    return f"uploads/{new_filename}"


def delete_uploaded_image(image_path):
    if not image_path or not image_path.startswith("uploads/"):
        return

    filename = image_path.split("/", 1)[1]
    file_path = UPLOAD_FOLDER / filename

    try:
        if file_path.is_file():
            file_path.unlink()
    except OSError:
        app.logger.warning("Could not delete image: %s", image_path)


# ==================== HOME ====================

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("todos"))
    return redirect(url_for("login"))


# ==================== REGISTER ====================

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name:
            error = "Name is required"
        elif not email:
            error = "Email is required"
        elif not password:
            error = "Password is required"
        elif not confirm_password:
            error = "Confirm password is required"
        elif password != confirm_password:
            error = "Passwords do not match"
        else:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                    if cursor.fetchone():
                        error = "Email Already Exists"
                    else:
                        password_hash = bcrypt.hashpw(
                            password.encode("utf-8"), bcrypt.gensalt()
                        ).decode("utf-8")

                        cursor.execute(
                            "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                            (email, name, password_hash),
                        )
                        connection.commit()
                        session["user_id"] = cursor.lastrowid
                        session["user_name"] = name
                        return redirect(url_for("todos"))
            finally:
                connection.close()

    return render_template("register.html", error=error)


# ==================== LOGIN ====================

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email:
            error = "Email is required"
        elif not password:
            error = "Password is required"
        else:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT user_id, name, password_hash FROM users WHERE email = %s",
                        (email,),
                    )
                    user = cursor.fetchone()

                    if not user or not bcrypt.checkpw(
                        password.encode("utf-8"), user["password_hash"].encode("utf-8")
                    ):
                        error = "Invalid email or password"
                    else:
                        session.clear()
                        session["user_id"] = user["user_id"]
                        session["user_name"] = user["name"]
                        return redirect(url_for("todos"))
            finally:
                connection.close()

    return render_template("login.html", error=error)


# ==================== LOGOUT ====================

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==================== TODOS LIST ====================

@app.route("/todos")
def todos():
    if "user_id" not in session:
        return redirect(url_for("login"))

    current_filter = request.args.get("filter", "all")
    search = request.args.get("search", "").strip()

    if current_filter not in ("all", "open", "done"):
        current_filter = "all"

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT todo_id, title, is_done, created_at, due_date FROM todos WHERE user_id = %s"
            params = [session["user_id"]]

            if current_filter == "open":
                query += " AND is_done = 0"
            elif current_filter == "done":
                query += " AND is_done = 1"

            if search:
                query += " AND title LIKE %s"
                params.append(f"%{search}%")

            query += " ORDER BY todo_id DESC"
            cursor.execute(query, params)
            todo_items = cursor.fetchall()

            cursor.execute(
                "SELECT COUNT(*) AS open_count FROM todos WHERE user_id = %s AND is_done = 0",
                (session["user_id"],),
            )
            open_count = cursor.fetchone()["open_count"]
    finally:
        connection.close()

    return render_template(
        "todos.html",
        todos=todo_items,
        user_name=session.get("user_name", ""),
        current_filter=current_filter,
        open_count=open_count,
        search=search,
    )


# ==================== ADD TODO ====================

@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    due_date = request.form.get("due_date", "").strip()

    if not title or len(title) > 200:
        return redirect(url_for("todos"))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO todos (user_id, title, due_date) VALUES (%s, %s, %s)",
                (session["user_id"], title, due_date or None),
            )
        connection.commit()
    finally:
        connection.close()

    return redirect(url_for("todos"))


# ==================== EDIT TODO ====================

@app.route("/todos/<int:todo_id>/edit", methods=["GET", "POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    error = None

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT todo_id, title, due_date FROM todos WHERE todo_id = %s AND user_id = %s",
                (todo_id, session["user_id"]),
            )
            todo = cursor.fetchone()

            if not todo:
                return "Todo not found", 404

            if request.method == "POST":
                title = request.form.get("title", "").strip()
                due_date = request.form.get("due_date", "").strip()

                if not title:
                    error = "Title is required"
                elif len(title) > 200:
                    error = "Title is too long"
                else:
                    cursor.execute(
                        "UPDATE todos SET title = %s, due_date = %s WHERE todo_id = %s AND user_id = %s",
                        (title, due_date or None, todo_id, session["user_id"]),
                    )
                    connection.commit()
                    return redirect(url_for("todos"))

                todo["title"] = title
                todo["due_date"] = due_date or None
    finally:
        connection.close()

    return render_template("edit_todo.html", todo=todo, error=error)


# ==================== DONE / UNDO TODO ====================

@app.route("/todos/<int:todo_id>/done", methods=["POST"])
def toggle_done(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    is_done = request.form.get("is_done", "0")
    if is_done not in ("0", "1"):
        return "Invalid status", 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
                (int(is_done), todo_id, session["user_id"]),
            )
        connection.commit()
    finally:
        connection.close()

    return redirect(url_for("todos"))


# ==================== DELETE TODO ====================

@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM todos WHERE todo_id = %s AND user_id = %s",
                (todo_id, session["user_id"]),
            )
        connection.commit()
    finally:
        connection.close()

    return redirect(url_for("todos"))


# ==================== LIBRARY ====================

@app.route("/library")
def library():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM AUTHOR ORDER BY author_id")
            authors = cursor.fetchall()

            cursor.execute("SELECT * FROM BOOK ORDER BY book_id")
            books = cursor.fetchall()
    finally:
        connection.close()

    return render_template("library.html", authors=authors, books=books)


# ==================== ADD / EDIT / DELETE AUTHOR ====================

@app.route("/authors/add", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()
        image = request.files.get("image")
        image_path = None

        if not name:
            return render_template("add_author.html", error="Author name is required")

        try:
            if image and image.filename:
                image_path = save_uploaded_image(image)

            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO AUTHOR (name, country, image_url) VALUES (%s, %s, %s)",
                        (name, country or None, image_path),
                    )
                connection.commit()
            finally:
                connection.close()
            return redirect(url_for("library"))
        except Exception as exc:
            if image_path:
                delete_uploaded_image(image_path)
            return render_template("add_author.html", error=str(exc))

    return render_template("add_author.html")


@app.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM AUTHOR WHERE author_id = %s", (author_id,))
            author = cursor.fetchone()

        if not author:
            return "Author not found", 404

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            country = request.form.get("country", "").strip()
            image = request.files.get("image")
            new_image_path = None

            if not name:
                return render_template("edit_author.html", author=author, error="Author name is required")

            if image and image.filename:
                new_image_path = save_uploaded_image(image)

            image_path = new_image_path or author.get("image_url")

            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE AUTHOR SET name = %s, country = %s, image_url = %s WHERE author_id = %s",
                    (name, country or None, image_path, author_id),
                )
            connection.commit()

            if new_image_path and author.get("image_url"):
                delete_uploaded_image(author.get("image_url"))

            return redirect(url_for("library"))
    finally:
        connection.close()

    return render_template("edit_author.html", author=author)


@app.route("/authors/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT image_url FROM AUTHOR WHERE author_id = %s", (author_id,))
            author = cursor.fetchone()
            image_path = author.get("image_url") if author else None

            cursor.execute("DELETE FROM AUTHOR WHERE author_id = %s", (author_id,))
        connection.commit()
    finally:
        connection.close()

    delete_uploaded_image(image_path)
    return redirect(url_for("library"))


# ==================== ADD / EDIT / DELETE BOOK ====================

@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT author_id, name FROM AUTHOR ORDER BY name")
            authors = cursor.fetchall()

            cursor.execute("SELECT publisher_id, name FROM PUBLISHER ORDER BY name")
            publishers = cursor.fetchall()

            cursor.execute("SELECT category_id, name FROM CATEGORY ORDER BY name")
            categories = cursor.fetchall()

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            price_text = request.form.get("price", "").strip()
            publish_year_text = request.form.get("publish_year", "").strip()
            author_id = request.form.get("author_id", "").strip()
            publisher_id = request.form.get("publisher_id", "").strip()
            category_id = request.form.get("category_id", "").strip()
            image = request.files.get("image")
            image_path = None

            if not title or not price_text or not author_id or not publisher_id or not category_id:
                return render_template(
                    "add_book.html",
                    authors=authors,
                    publishers=publishers,
                    categories=categories,
                    error="All required fields must be filled",
                )

            try:
                price = float(price_text)
                if price < 0:
                    return render_template(
                        "add_book.html",
                        authors=authors,
                        publishers=publishers,
                        categories=categories,
                        error="Price cannot be negative",
                    )
            except ValueError:
                return render_template(
                    "add_book.html",
                    authors=authors,
                    publishers=publishers,
                    categories=categories,
                    error="Invalid price value",
                )

            publish_year = int(publish_year_text) if publish_year_text else None

            if image and image.filename:
                image_path = save_uploaded_image(image)

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO BOOK (title, price, publish_year, author_id, publisher_id, category_id, image_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (title, price, publish_year, author_id, publisher_id, category_id, image_path),
                )
            connection.commit()
            return redirect(url_for("library"))
    finally:
        connection.close()

    return render_template(
        "add_book.html",
        authors=authors,
        publishers=publishers,
        categories=categories,
    )


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM BOOK WHERE book_id = %s", (book_id,))
            book = cursor.fetchone()

            cursor.execute("SELECT author_id, name FROM AUTHOR ORDER BY name")
            authors = cursor.fetchall()

            cursor.execute("SELECT publisher_id, name FROM PUBLISHER ORDER BY name")
            publishers = cursor.fetchall()

            cursor.execute("SELECT category_id, name FROM CATEGORY ORDER BY name")
            categories = cursor.fetchall()

        if not book:
            return "Book not found", 404

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            price_text = request.form.get("price", "").strip()
            publish_year_text = request.form.get("publish_year", "").strip()
            author_id = request.form.get("author_id", "").strip()
            publisher_id = request.form.get("publisher_id", "").strip()
            category_id = request.form.get("category_id", "").strip()
            image = request.files.get("image")
            new_image_path = None

            if not title or not price_text or not author_id or not publisher_id or not category_id:
                return render_template(
                    "edit_book.html",
                    book=book,
                    authors=authors,
                    publishers=publishers,
                    categories=categories,
                    error="All required fields must be filled",
                )

            try:
                price = float(price_text)
                if price < 0:
                    return render_template(
                        "edit_book.html",
                        book=book,
                        authors=authors,
                        publishers=publishers,
                        categories=categories,
                        error="Price cannot be negative",
                    )
            except ValueError:
                return render_template(
                    "edit_book.html",
                    book=book,
                    authors=authors,
                    publishers=publishers,
                    categories=categories,
                    error="Invalid price value",
                )

            publish_year = int(publish_year_text) if publish_year_text else None

            if image and image.filename:
                new_image_path = save_uploaded_image(image)

            image_path = new_image_path or book.get("image_url")

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE BOOK
                    SET title = %s, price = %s, publish_year = %s,
                        author_id = %s, publisher_id = %s, category_id = %s, image_url = %s
                    WHERE book_id = %s
                    """,
                    (title, price, publish_year, author_id, publisher_id, category_id, image_path, book_id),
                )
            connection.commit()

            if new_image_path and book.get("image_url"):
                delete_uploaded_image(book.get("image_url"))

            return redirect(url_for("library"))
    finally:
        connection.close()

    return render_template(
        "edit_book.html",
        book=book,
        authors=authors,
        publishers=publishers,
        categories=categories,
    )





@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT image_url FROM BOOK WHERE book_id = %s", (book_id,))
            book = cursor.fetchone()
            image_path = book.get("image_url") if book else None

            cursor.execute("DELETE FROM BOOK WHERE book_id = %s", (book_id,))
        connection.commit()
    finally:
        connection.close()

    delete_uploaded_image(image_path)
    return redirect(url_for("library"))

# ==================== LAB 4: SEARCH & REPORT PAGES (F2.1 - F2.6) ====================

@app.route("/search")
def search_books():
    keyword = request.args.get("keyword", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    category_id = request.args.get("category_id", "").strip()

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT category_id, name FROM CATEGORY ORDER BY name")
            categories = cursor.fetchall()

            # Parameterized query (Bonus: Prepared Statements)
            query = """
                SELECT b.book_id, b.title, b.price, b.publish_year,
                       a.name AS author_name, c.name AS category_name
                FROM BOOK b
                JOIN AUTHOR a ON b.author_id = a.author_id
                JOIN CATEGORY c ON b.category_id = c.category_id
                WHERE 1=1
            """
            params = []

            if keyword:
                query += " AND b.title LIKE %s"
                params.append(f"%{keyword}%")

            if min_price and max_price:
                query += " AND b.price BETWEEN %s AND %s"
                params.extend([float(min_price), float(max_price)])
            elif min_price:
                query += " AND b.price >= %s"
                params.append(float(min_price))
            elif max_price:
                query += " AND b.price <= %s"
                params.append(float(max_price))

            if category_id:
                query += " AND b.category_id = %s"
                params.append(int(category_id))

            query += " ORDER BY b.price ASC"
            cursor.execute(query, params)
            books = cursor.fetchall()
    finally:
        connection.close()

    return render_template(
        "search_books.html",
        books=books,
        categories=categories,
        keyword=keyword,
        min_price=min_price,
        max_price=max_price,
        selected_category=category_id,
    )


@app.route("/catalogue")
def catalogue():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.book_id, b.title, b.price, b.publish_year,
                       a.name AS author_name,
                       p.name AS publisher_name,
                       c.name AS category_name
                FROM BOOK b
                JOIN AUTHOR a ON b.author_id = a.author_id
                JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
                JOIN CATEGORY c ON b.category_id = c.category_id
                ORDER BY b.book_id ASC
            """)
            books = cursor.fetchall()
    finally:
        connection.close()

    return render_template("catalogue.html", books=books)


@app.route("/reports")
def reports():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # F2.3 (a)
            cursor.execute("""
                SELECT c.name AS category_name, COUNT(b.book_id) AS book_count, AVG(b.price) AS avg_price
                FROM CATEGORY c
                LEFT JOIN BOOK b ON c.category_id = b.category_id
                GROUP BY c.category_id, c.name
            """)
            category_stats = cursor.fetchall()

            # F2.3 (b)
            cursor.execute("""
                SELECT a.name AS author_name, COUNT(b.book_id) AS book_count
                FROM AUTHOR a
                JOIN BOOK b ON a.author_id = b.author_id
                GROUP BY a.author_id, a.name
                HAVING COUNT(b.book_id) >= 2
            """)
            prolific_authors = cursor.fetchall()

            # F2.3 (c)
            cursor.execute("""
                SELECT SUM(price) AS total_price, MIN(price) AS min_price, MAX(price) AS max_price
                FROM BOOK
            """)
            library_totals = cursor.fetchone()
    finally:
        connection.close()

    return render_template(
        "reports.html",
        category_stats=category_stats,
        prolific_authors=prolific_authors,
        library_totals=library_totals,
    )


@app.route("/loans")
def loans():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # F2.4 (a) Active loans
            cursor.execute("""
                SELECT l.loan_id, b.title AS book_title, m.name AS member_name, l.loan_date
                FROM LOAN l
                JOIN BOOK b ON l.book_id = b.book_id
                JOIN MEMBER m ON l.member_id = m.member_id
                WHERE l.return_date IS NULL
                ORDER BY l.loan_date ASC
            """)
            active_loans = cursor.fetchall()

            # F2.4 (b) Members who never borrowed
            cursor.execute("""
                SELECT m.member_id, m.name, m.email, m.join_date
                FROM MEMBER m
                LEFT JOIN LOAN l ON m.member_id = l.member_id
                WHERE l.loan_id IS NULL
            """)
            inactive_members = cursor.fetchall()

            # F2.4 (c) Books never borrowed
            cursor.execute("""
                SELECT b.book_id, b.title, b.price, b.publish_year
                FROM BOOK b
                LEFT JOIN LOAN l ON b.book_id = l.book_id
                WHERE l.loan_id IS NULL
            """)
            unborrowed_books = cursor.fetchall()
    finally:
        connection.close()

    return render_template(
        "loans.html",
        active_loans=active_loans,
        inactive_members=inactive_members,
        unborrowed_books=unborrowed_books,
    )


@app.route("/most-borrowed")
def most_borrowed():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # F2.5 (a) Top 3 books
            cursor.execute("""
                SELECT b.title, COUNT(l.loan_id) AS loan_count
                FROM BOOK b
                JOIN LOAN l ON b.book_id = l.book_id
                GROUP BY b.book_id, b.title
                ORDER BY loan_count DESC
                LIMIT 3
            """)
            top_books = cursor.fetchall()

            # F2.5 (b) Top member
            cursor.execute("""
                SELECT m.name, COUNT(l.loan_id) AS loan_count
                FROM MEMBER m
                JOIN LOAN l ON m.member_id = l.member_id
                GROUP BY m.member_id, m.name
                ORDER BY loan_count DESC
                LIMIT 1
            """)
            top_member = cursor.fetchone()
    finally:
        connection.close()

    return render_template("most_borrowed.html", top_books=top_books, top_member=top_member)


@app.route("/authors-books")
def authors_books():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # F2.6 (a) All authors with book count
            cursor.execute("""
                SELECT a.author_id, a.name, a.country, COUNT(b.book_id) AS book_count
                FROM AUTHOR a
                LEFT JOIN BOOK b ON a.author_id = b.author_id
                GROUP BY a.author_id, a.name, a.country
                ORDER BY book_count DESC
            """)
            author_counts = cursor.fetchall()

            # F2.6 (b) Books where author & publisher share country
            cursor.execute("""
                SELECT b.title, a.name AS author_name, p.name AS publisher_name, a.country
                FROM BOOK b
                JOIN AUTHOR a ON b.author_id = a.author_id
                JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
                WHERE a.country = p.country
            """)
            same_country_books = cursor.fetchall()
    finally:
        connection.close()

    return render_template(
        "authors_books.html",
        author_counts=author_counts,
        same_country_books=same_country_books,
    )
# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    app.run(debug=True)