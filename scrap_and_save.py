import pandas as pd
from scrape import summary_finder
from concurrent.futures import ThreadPoolExecutor, as_completed
import pyisbn
import math
import sys
import os
import shutil

def norm_isbn(isbn):
    isbn = str(isbn)
    if len(isbn) < 10:
        isbn = f"{'0' * (10-len(isbn))}{isbn}"
    if len(isbn) == 10:
        try:
            new_isbn = pyisbn.convert(isbn)
        except:
            return isbn
    else:
        new_isbn = isbn
    return new_isbn

def scrap_and_save(data_table_path, start_idx=0):
    if data_table_path[-4:] == '.csv':
        data_table = pd.read_csv(data_table_path)
    else:
        data_table = pd.read_excel(data_table_path)
    try:
        os.makedirs(f"{data_table_path.split('.')[0]}")
    except:
        pass
    for i in range(start_idx, math.ceil(len(data_table)/10)):
        print(f"{i*10}/{len(data_table)}")
        books = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(summary_finder, isbn)
                for isbn in data_table['ISBN'][10*i:10*(i+1)]
            ]
            
            for future in as_completed(futures):
                isbn, keywords, summary = future.result()
                books.append({
                    'isbn': isbn,
                    'keywords': keywords,
                    'summary': summary,
                    'norm isbn': norm_isbn(isbn),
                    'chunk': i
                })
        pd.DataFrame(books).to_excel(f'{data_table_path.split(".")[0]}/{i}.xlsx', index=False)
    print(f"All data scraped")
        
def merger(data_table_path):
    if data_table_path[-4:] == '.csv':
        data_table = pd.read_csv(data_table_path)
    else:
        data_table = pd.read_excel(data_table_path)
    data_columns = [col for col in data_table.columns]
    data_table['chunk'] = (data_table['Index'] - 1) // 10
    data_table['norm isbn'] = data_table['ISBN'].apply(norm_isbn)
    
    folder_name = data_table_path.split('.')[0]
    
    book_table = pd.DataFrame(columns=['isbn', 'keywords', 'summary', 'norm isbn', 'chunk'])
    for chunk in range(math.ceil(len(data_table)/10)):
        book_chunk = pd.read_excel(f"{folder_name}/{chunk}.xlsx")
        book_table = pd.concat([book_table, book_chunk], ignore_index=True)
    book_table.reset_index(drop=True, inplace=True)
    book_table['chunk'] = book_table['chunk'].astype(int)
    book_table['norm isbn'] = book_table['norm isbn'].astype(str)
    merged = data_table.merge(book_table, on=['chunk', 'norm isbn'], how='left')
    data_columns.extend(['keywords', 'summary', 'norm isbn'])
    merged = merged.drop_duplicates(subset=['Index'], keep='first', ignore_index=True)[data_columns]
    merged.rename(columns={'norm isbn': 'isbn13'}, inplace=True)
    merged.to_excel(f'{folder_name}_output.xlsx', index=False)

    print(f"Files merged into {folder_name}_output.xlsx")
    shutil.rmtree(f'{folder_name}')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        data_path = sys.argv[1]
        scrap_and_save(data_path)
        merger(data_path)
    elif len(sys.argv) == 3:
        data_path = sys.argv[1]
        idx = int(sys.argv[2])
        scrap_and_save(data_path, start_idx=idx)
        merger(data_path)
    else:
        print("Usage: python scrap_and_save.py <relative_path_of_isbn_source> [start_idx=0]")
    