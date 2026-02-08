from requests import request
from bs4 import BeautifulSoup
import pyisbn
import sys

# Using Google API, OpenLibrary API and bookwagon.com

def summary_finder(isbn):
    header = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0'}
    
    summary = ""
    keywords = []        
    isbn = str(isbn)
    if len(isbn) < 10:
        isbn = f"{'0'*(10 - len(isbn))}{isbn}"
    
    # print("openLibrary")
    api_link = f"https://www.openlibrary.org/isbn/{isbn}.json"
    api_req = request(method="GET", url=api_link, headers=header)
    try:
        # print("Trying json")
        # print(api_req)
        api_res = api_req.json()
        if 'subjects' in api_res:
            # print("Found subjects")
            keywords = api_res['subjects']
        if 'description' in api_res:
            # print("Found desc")
            if type(api_res['description']) == dict:
                summary = api_res['description']['value']
            else:
                summary = api_res['description']
        if not summary and 'first_sentence' in api_res:
            # print("Found first sentence")
            if type(api_res['first_sentence']) == dict:
                summary = api_res['first_sentence']['value']
            else:
                summary = api_res['first_sentence']
        if 'works' in api_res:
            # print("Going in works")
            api_link = f"https://www.openlibrary.org{api_res['works'][0]['key']}.json"
            api_req = request(method="GET", url = api_link, headers=header)
            api_res = api_req.json()
            if 'subjects' in api_res:
                if len(keywords) < len(api_res['subjects']):
                    keywords = api_res['subjects']
            if 'description' in api_res:
                if type(api_res['description']) == dict and len(api_res['description']['value']) > len(summary):
                    summary = api_res['description']['value']
                else:
                    if len(api_res['description']) > len(summary):
                        summary = api_res['description']
        summary = BeautifulSoup(summary, 'html.parser')
        summary = summary.text.replace('\n', ' ')
        if summary and keywords:
            return isbn, ', '.join(keywords), summary
    except:
        pass
    
    # print("Trying bookswagon")
    if len(isbn) == 10:
        try:
            isbn = pyisbn.convert(isbn)
            # print('new isbn', isbn)
        except:
            return isbn, "", ""
    search_base_link = f'https://www.bookswagon.com/book/c/{isbn}'
    search_req = request(method='GET', url=search_base_link, headers=header)
    book_soup = BeautifulSoup(search_req.text, 'html.parser')
    new_summary = book_soup.find(name='div', attrs={'id': 'aboutbook'})
    # print('new_summary', new_summary)
    if new_summary:
        new_summary = new_summary.p
        new_summary = new_summary.text.replace('\n', ' ')
        if len(summary) < len(new_summary.strip()):
            summary = new_summary.strip()
    cats = book_soup.find('ul', attrs={'class': 'blacklistreview'})
    if cats:
        cats = cats.find_all('a')
        cats = list({k.text.strip() for k in cats})
        if len(cats) > len(keywords):
            keywords = cats
    if keywords and summary:
        return isbn, ', '.join(keywords), summary
    
    # print('Trying google')
    
    api_link = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    api_req = request(method='GET', url=api_link, headers=header)
    api_res = api_req.json()
    if 'totalItems' in api_res and api_res['totalItems'] != 0:
        if 'description' in api_res['items'][0]['volumeInfo'] and len(summary) < len(api_res['items'][0]['volumeInfo']['description']):
            summary = api_res['items'][0]['volumeInfo']['description']
        if 'categories' in api_res['items'][0]['volumeInfo'] and len(keywords) < len(api_res['items'][0]['volumeInfo']['categories']):
            keywords = api_res['items'][0]['volumeInfo']['categories']
    
    return isbn, ', '.join(keywords), summary

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scrape.py <isbn>")
    else:
        print(f"{summary_finder(sys.argv[1])}")