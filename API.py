from fastapi import FastAPI, HTTPException, Query
import sqlite3

app = FastAPI(
    title="Book Information API",
    description="API to fetch books data from a server",
    version='1.0.0'
)

DB_PATH = "books.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def root():
    return {
        "message": "Book API is up"
        }


@app.get("/books")
def get_books(
    limit: int = Query(None, ge=1, le=10906, description="Number of books to fetch (leave empty if trying to fetch all)")
):
    conn = get_db_connection()
    cursor = conn.cursor()

    if limit is None:
        cursor.execute("""
            SELECT *
            FROM book
            WHERE description IS NOT NULL
            ORDER BY AccDate DESC
        """)
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"code": 200, "count": len(books), "data":books}
        
    cursor.execute("""
        SELECT *
        FROM book
        WHERE description IS NOT NULL
        ORDER BY AccDate DESC
        LIMIT ?
    """, (limit, ))

    books = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {
        "code": 200,
        "count": len(books),
        "data": books
    }

@app.get("/books/{isbn}")
def get_book_by_isbn_path(isbn: str):
    isbn = isbn.strip().replace("-", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM book
        WHERE ISBN = ?
    """, (isbn,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return dict(row)