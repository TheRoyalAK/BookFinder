import pandas as pd
import sqlite3

books_data = pd.read_excel('./Final_Data.xlsx')

conn = sqlite3.connect('books.db')

books_data.to_sql('book', conn, if_exists='replace', index=False)

print("books.db created!")

conn.commit()
conn.close()
