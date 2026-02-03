<h1 align = 'center'> Book Finder </h1>

<p align='right'> Anish Karmakar - 202518061<br> Shah Trush - 202518027</p>

> [!NOTE]
> This project is about building a robust data pipeline to extract, clean, and store book information (titles, descriptions, genres) to provide a high-quality dataset for an ML-powered semantic search system.

## Table of Contents
- [Project Objectives](#project-objectives)
- [Data Ingestion](#data-ingestion)
  - [Problems in the Raw Dataset](#problems-in-the-raw-dataset)
  - [External Data Sources](#external-data-sources)
  - [Scraping Strategy](#scraping-strategy)
- [Transformation](#transformation)
- [Storage](#storage)
  - [Standardized Schema](#standardized-schema)
- [API Serving (FastAPI)](#api-serving-fastapi)
- [Tech Stack](#tech-stack)
- [File Descriptions](#file-descriptions)
- [Final Data Statistics](#final-data-statistics)
- [Setup](#setup)
  - [Prerequisites](#one-time-installation-of-required-libraries)
  - [Methods](#to-setup-the-server-in-your-local-system-there-are-two-methods-depending-on-your-need)
- [Workflow](#workflow)

## Project Objectives

- Ingest raw book data with inconsistent formats
- Clean and standardize metadata fields
- Enrich book records using external sources
- Store structured data in a relational database
- Serve data via RESTful endpoints

## Data Ingestion

Initial data was taken from the College RC.

### Problems in the Raw Dataset

The initial CSV provided by the Resource Center (RC) contained multiple issues:

```text
?C++        → C++
?????, ???????? ???????? / Munashi, Kanaiyalal Maneklal
Missing ISBNs
Inconsistent author formatting
```

### External Data Sources

- OpenLibrary       → Extensive coverage and summaries ("https://www.openlibrary.org/isbn/{isbn}.json")

- Bookswagon        → Fallback for missing details ("https://www.bookswagon.com/books/c/{isbn}")

- Google Books API  → Fast metadata retrieval ("https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")

Data was fetched using HTTP GET requests and parsed with BeautifulSoup.

Open the `FinalScraper.ipynb` for more information about the whole process.

### Scraping Strategy

- Query OpenLibrary for the summary & keywords

- If anything is missing, fallback to Bookswagon

- If anything still remains, fallback to Google API (last due to API key Quota limits)

- Prefer longer and more descriptive summaries

- Return empty values if no data is found

Challanges

- Scraper instability

- Inconsistent HTML structures

- Time constraints

## Transformation

* Removed ?? (placeholder for different language texts e.g. Devanagari, Vardana, etc)
* Fixed a few ISBNs that had typos.
* Fixed publisher location
* Fixed Accession Dates
* Ed./Vol. was merged with Title
* Removed \n and some html tags from summaries

## Storage
Database: `SQLite3`

Method: `pandas.DataFrame.to_sql()`

### Standardized Schema:
Column Name| Column Description | Type | Null Counts
---|---|---|---
AccNo|Accession Number| `int64`| 0
AccDate| Accession Date | `str` | 144
Title|Name of the book | `str` | 0
ISBN|ISBN of the book (given by RC) | `str` | 0
ISBN13|ISBN13 of the book | `str` | 0
Author|Author of the book | `str` | 0
Publisher|Place and publisher of the book | `str` | 0
Year|Year of publishing the book | `float64` | 7
Pages|Number of pages in the book | `str` | 105
DDC|Class No./Book No. provided by the RC | `str` | 0
Keywords|Special keywords of the book (e.g. category, genre, etc) | `str` | 4268
Summary|Description about the book | `str` | 4011

## API Serving (FastAPI)
End Points

 - `/`  for learning about FastAPI, to see whether it works or not.
   
 - `/books` this endpoint has an optional parameter limit, if left empty, it will fetch all the books in the database, and if given a value, it will fetch the latest books as per the value given.
   
 - `/books/{ID}` This endpoint searches for the given `ID` (which can be either AccNo, ISBN, ISBN13 or DDC) in the DB and returns all the book details associated with it.

## Tech Stack
- Python     
- Pandas     
- BeautifulSoup     
- SQLite3     
- FastAPI   


## File Descriptions
File name | File Description
---|---
`Accession Register-Books_with_ISBN_numbers.csv`|file provided by the RC.
`Accession Register-Books_with_ISBN_numbers.xlsx`|cleaned file in `.xlsx`
`AccNoISBN.ipynb`|The raw `.ipynb` which we worked in (not that readable due to many tests).
`API.py`|Contains the FastAPI code to run the server.
`books.db`|The database created using SQLite3.
`Final_Data.xlsx`|Final data that was stored in the database.
`Final_scraper.ipynb`|Readable version of `AccNoISBN.ipynb`.
`NoISBN.xlsx`|Books that have wrong ISBN or None as their ISBN.
`post_to_db.py`|Python file to convert `Final_Data.xlsx` into `books.db` using SQLite3 and Pandas.
`requirements.txt`|Requirements for setting up the server in the local system.
`./Summaries/`|Contains the summaries of all the books (in batches of 10) made by using the `scrap_and_save()` function inside `Final_scraper.ipynb`.
`./Extra/`|Contains the files that were made when scraping from the RC website (was not used later).



## Final Data Statistics

Type of Data | Number of books | Percentage of books
---|---|---
Total books with unique ISBNs|31532
Books with no summaries|4006 |12.70%
Books with no keywords|4268 |13.54%
Books with neither summary nor keywords|3391 |10.75%
Books with both summary and keywords|26649 |84.51%

## Setup

It is not recommended to scrape for the data again, as it took 17 hours to scrape this detailed data. And hence the modules for that are not written inside `requirements.txt`.

If you still want to execute the whole procedure on your system, follow the instructions mentioned in the section [Workflow](#workflow).

### Prerequisites

In a command prompt shell, open the repository folder and run `pip install -r requirements.txt`


### To setup the server in your local system, there are two methods depending on your needs:

* If you are okay with hosting the server at `127.0.0.1:8000`:
  1. Open Command Prompt in the folder where `API.py` is located.
  2. Run `python API.py`
  3. The server has started at `127.0.0.1:8000` !

* If you want to host the server at your own choice of address and port:
  1. Open Command Prompt in the folder where `API.py` is located.
  2. Run `uvicorn API:app --host <address> --port <port>`
  3. Now the server has started at the address and port of your choice!


## Workflow

If you want to do the whole process again and on your own, follow these instructions:

1. Install the required libraries using `pip`
    - To identify the required libraries, open `FinalScraper.ipynb` and check the __Useful Imports__ section for all the libraries used.
2. Clean your source data as needed and make sure to convert it into `.xlsx` (Generally better for complex texts than `.csv` due to delimiters).
3. Start running the cells inside `FinalScraper.ipynb` one by one.
    - While doing this, you might get into errors like "No file found" or "Key Error", in that case check if your data has the same structure and name as `Accession Register-Books_with_ISBN_numbers.xlsx`.
4. After executing all the cells you will now have `Final_Data.xlsx`.
    - Optional: You can clean this more using Excel tricks.
5. Now open command prompt and run `python post_to_db.py` to make the database file.
6. For further help, go [here](#to-setup-the-server-in-your-local-system-there-are-two-methods-depending-on-your-need).
