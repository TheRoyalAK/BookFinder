<h1 align = 'center'> Book Finder </h1>

<p align='right'> Anish Karmakar - 202518061<br> Shah Trush - 202518027</p>

----------------------------
> [!NOTE]
> This project is about building a robust data pipeline to extract, clean, and store book information (titles, descriptions, genres) to provide a high-quality dataset for an ML-powered semantic search system.
----------------------------

## Project Objectives

- Ingest raw book data with inconsistent formats
- Clean and standardize metadata fields
- Enrich book records using external sources
- Store structured data in a relational database
- Serve data via RESTful endpoints

---

## Data Ingestion

### Problems in the Raw Dataset

The initial CSV provided by the Resource Center (RC) contained multiple issues:

```text
?C++        → C++
?????, ???????? ???????? / Munashi, Kanaiyalal Maneklal
Missing ISBNs
Inconsistent author formatting
```

## Standardized Schema
- Accession Number
- Accession Date
- Book Title
- ISBN
- Author / Editor
- Place & Publisher
- Year
- Pages
- Class No / Book No
- Category
- Summary / Description

## External Data Sources
Google Books API  → Fast metadata retrieval

https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}

OpenLibrary       → Extensive coverage and summaries

https://www.openlibrary.org/isbn/{isbn}.json

Bookswagon        → Fallback for missing details

https://www.bookswagon.com/books/c/{isbn}

Data was fetched using HTTP GET requests and parsed with BeautifulSoup.

Open the `FinalScraper.ipynb` for more information about the whole process.

## ⚠️ Data Corruption Incident
- A critical issue occurred during data cleaning due to incorrect file handling:

  > ❌ Incorrect 

   pd.read_csv("books.xlsx")

  > ✅ Correct

   pd.read_excel("books.xlsx")

- This resulted in Excel file corruption and required rebuilding the dataset.

- Lesson learned: Always validate file formats and maintain backups during transformation.

## Transformation
Scraping Strategy

- Query Google API for summary & keywords

- Query OpenLibrary for the same

- If missing, fallback to Bookswagon

- Prefer longer and more descriptive summaries

- Return empty values if no data is found

Challanges

- Scraper instability

- Inconsistent HTML structures

- Time constraints

### The dataset was completed through <I> collaboration </I> after optimization attempts.

## Storage
Database: SQLite3

Method: pandas.DataFrame.to_sql()

## API Serving (FastAPI)
End Points

 - "/"  for learning about FastAPI, to see whether it works or not.
   
 - "/books" this endpoint has an optional parameter limit, if left empty, it will fetch all the books in the database, and if given a value, it will fetch the latest books as per the value given.
   
 - /books/{isbn}" This endpoint searches for the given ISBN in the DB and returns all the book details associated with it.

## Tech Stack
- Python     
- Pandas     
- BeautifulSoup     
- SQLite3     
- FastAPI     
- REST APIs     
## 
