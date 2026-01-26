import pandas as pd
import sqlite3

books_data = pd.read_excel('./Final_cleaned_data.xlsx')

conn = sqlite3.connect('books.db')

books_data.to_sql('book', conn, if_exists='replace', index=False)

result = pd.read_sql_query("SELECT * from book", conn)

print(result)

conn.commit()
conn.close()