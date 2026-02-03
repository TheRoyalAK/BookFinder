# LLM Usage log

When working on this project we used LLMs for minor bug fixes and to use multithreading in our code which is shown below.

# Prompt 1
How to use multi threading in this code:
```python
search_base_link = 'https://www.google.com/search?tbo=p&tbm=bks&q=isbn:'
for isbn in data_table['ISBN'][:20]:
    isbn = str(isbn)
    while len(isbn) < 10:
        isbn = "0" + isbn
    print(isbn)
    
    search_req = request(method='GET', url=f"{search_base_link}{isbn}", headers=header)
    search_soup = BeautifulSoup(search_req.text, 'html.parser')
    link = search_soup.find('a', {'href': True, 'jsname': 'UWckNb'}).attrs['href'].split('&')[0]
    book_req = request('GET', link, headers=header)
    book_soup = BeautifulSoup(book_req.text, 'html.parser')
    summary = book_soup.find(name='div', attrs={'id': 'synopsistext'})
    if not summary:
        summary = book_soup.find(name='div', attrs={'class': 'Mhmsgc'})
    for br in summary.find_all('br'):
        br.replace_with('\\n')
    print(summary.text)
```
## Answer
This is a **classic I/O-bound task** (lots of HTTP requests + parsing), so **multithreading is appropriate** 👍
In Python, the **cleanest and safest way** is `concurrent.futures.ThreadPoolExecutor`.

Below is a **minimal, correct refactor** of *your exact logic* into a threaded version.



### Step 1: Put the work for ONE ISBN into a function

Threads run functions, not loops.

```python
from requests import request
from bs4 import BeautifulSoup

search_base_link = 'https://www.google.com/search?tbo=p&tbm=bks&q=isbn:'

def fetch_summary(isbn, header):
    isbn = str(isbn)
    while len(isbn) < 10:
        isbn = "0" + isbn

    try:
        # Google Books search
        search_req = request(
            method='GET',
            url=f"{search_base_link}{isbn}",
            headers=header,
            timeout=10
        )
        search_soup = BeautifulSoup(search_req.text, 'html.parser')

        a_tag = search_soup.find('a', {'href': True, 'jsname': 'UWckNb'})
        if not a_tag:
            return isbn, None

        link = a_tag['href'].split('&')[0]

        # Book page
        book_req = request('GET', link, headers=header, timeout=10)
        book_soup = BeautifulSoup(book_req.text, 'html.parser')

        summary = book_soup.find('div', {'id': 'synopsistext'})
        if not summary:
            summary = book_soup.find('div', {'class': 'Mhmsgc'})
        if not summary:
            return isbn, None

        for br in summary.find_all('br'):
            br.replace_with('\n')

        return isbn, summary.text.strip()

    except Exception as e:
        return isbn, f"ERROR: {e}"
```



### Step 2: Run it using ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

results = {}

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(fetch_summary, isbn, header)
        for isbn in data_table['ISBN'][:20]
    ]

    for future in as_completed(futures):
        isbn, summary = future.result()
        results[isbn] = summary
        print(isbn)
        print(summary)
        print("-" * 40)
```



### Why this works well

* ✔ **Threads overlap waiting time** (HTTP requests)
* ✔ No GIL issues (network I/O releases GIL)
* ✔ Clean error handling
* ✔ Easy to control speed via `max_workers`


### Important ⚠️ (VERY relevant to your earlier Google API quota question)

Google **will throttle or block you** if you use too many threads.

#### Recommended:

* `max_workers = 3–5`
* Add headers properly (User-Agent)
* Consider adding a small delay if you see 429s

```python
import time
time.sleep(0.2)
```

inside `fetch_summary` if needed.


### If you want EVEN FASTER (advanced)

* Use `requests.Session()` per thread
* Or switch to `aiohttp` (async, harder but faster)

If you want, I can:

* Convert this to **async/await**
* Add **retry + backoff**
* Add **rate-limit protection**
* Store results directly into your dataframe

Just tell me 👍

# Prompt 2
Google says google book api gives the quota limit of 1000 per day... But I already scrapped 1300 and it's still scrapping... How does that work?

## Answer
This is a **very common confusion with Google Books API**, and the short answer is: **you’re probably not actually hitting the quota you think you are**.

Let’s break it down clearly.


### 1. The “1000 per day” limit is often misunderstood

Google Books API quotas have **multiple layers**, not just one simple “1000 requests/day”.

#### What Google usually means:

* **Requests per day** (e.g., 1000)
* **Requests per 100 seconds per user**
* **Requests per 100 seconds per project**

If you’re exceeding 1300 requests and it still works, one of these is true 👇


### 2. You may be using the API **without an API key**

If you make requests like:

```
https://www.googleapis.com/books/v1/volumes?q=python
```

(without `key=YOUR_API_KEY`)

Then:

* Requests are treated as **unauthenticated**
* They fall under a **shared public quota**
* Google is more lenient (but throttles silently if abused)

👉 Result: You can often exceed 1000 requests without errors.


### 3. The quota is per **project**, not per script or IP

If you **are using an API key**:

* Quota applies to the **Google Cloud project**
* Not per machine
* Not per program
* Not per IP

So if:

* You regenerated the key
* Or switched projects
* Or used multiple keys

👉 You might still be under quota **per project**


### 4. Search requests vs volume detail requests

This is a BIG one.

Example:

```http
/volumes?q=machine+learning
```

returns **up to 40 books per request**

So:

* 1 API call ≠ 1 book
* 1300 books scraped ≠ 1300 API requests

You might have made:

* 50–100 API calls
* But extracted 1300 book entries

👉 This is the **most common reason** people think they exceeded quota.


### 5. Google allows “soft overages”

Google often:

* Lets you temporarily exceed quota
* Does NOT immediately block
* Enforces limits via **slowing**, not hard errors

You’ll notice:

* Requests start taking longer
* Eventually get `429: Too Many Requests`

This is intentional to prevent sudden breakage.


### 6. Where to check your *actual* quota usage

Go to:

```
Google Cloud Console
→ APIs & Services
→ Google Books API
→ Quotas
```

You’ll see:

* Requests/day used
* Requests/100 seconds
* Whether limits are enforced or adjustable


### 7. Scraping vs API usage (important distinction)

If you are:

* **Scraping books.google.com HTML pages**

Then:
❌ You are **not using the Books API**
❌ API quotas do not apply at all
⚠️ You are subject to bot detection instead

Only URLs like:

```
www.googleapis.com/books/v1/...
```

count toward API quota.


### TL;DR

You can exceed “1000 books” because:

* Quota is **per API request**, not per book
* You may not be using an API key
* You may be under a different quota tier
* Google allows temporary overages
* Or you’re scraping HTML, not the API


If you want, paste:

* The exact URL you’re calling
* Whether you use an API key
* Rough code snippet (Python preferred 😉)

And I’ll tell you **exactly** which case applies to you.


# Prompt 3
if I use multithreading to scrap something off of google books website, will I get banned/blocked?

## Answer
Short answer: **yes, you *can* get blocked**, and **multithreading increases the risk** — but it’s not automatic, and it depends *how* you do it.

Let’s break it down clearly.


### 1. Multithreading itself is not the problem

Google doesn’t care whether requests come from:

* one thread
* multiple threads
* async code

What they **do care about** is:

* **request rate**
* **request patterns**
* **behavior that looks non-human**

Multithreading just makes it *very easy* to cross those limits accidentally.


### 2. What Google Books actually enforces

If you’re scraping the **website** (HTML pages, not the API), Google uses:

#### 🚨 Signals that trigger blocking

* Too many requests per second from the same IP
* Bursty traffic (e.g., 20 requests at once)
* Repeated identical headers (default Python `requests`)
* No cookies / no JS execution
* Hitting predictable URL patterns very fast
* Ignoring `robots.txt`

#### 🧱 What “blocked” usually looks like

* HTTP `429 Too Many Requests`
* CAPTCHA page
* Silent throttling (responses slow down)
* Temporary IP ban (minutes → hours → sometimes days)

**Account bans are extremely rare** — it’s almost always IP-based.


### 3. Google Books API vs Website scraping (important)

#### ✅ Google Books API

* Official
* Clear quota (e.g., 1000/day)
* Multithreading is usually fine **within quota**
* You already noticed it allows some overrun due to:

  * per-minute limits
  * delayed quota enforcement
  * cached responses

👉 **Best choice if possible**

#### ❌ Scraping the website

* Against Google’s ToS
* No guaranteed limits
* Much stricter anti-bot detection
* Multithreading = higher risk


### 4. Will multithreading get you banned?

#### ❌ High risk if you do this:

```text
10–50 threads
No delays
Same headers
No cookies
Running for minutes continuously
```

#### ✅ Low risk if you do this:

* 2–4 threads max
* Global rate limit (e.g. 1–2 req/sec total)
* Randomized delays
* Browser-like headers
* Session reuse

**Key idea:**

> Google measures **requests per IP per time window**, not threads.


### 5. Practical “safe-ish” guidelines

If you *must* scrape:

#### Threading

* Prefer **rate-limited threading**, not fire-and-forget
* Example rule of thumb:

  * `max 2–3 requests/second total`
  * regardless of thread count

#### Headers

* Real User-Agent
* Accept-Language
* Referer
* Keep cookies

#### Timing

* Random sleep (e.g. 0.5–1.5s)
* Avoid fixed intervals

#### Architecture tip

Instead of raw multithreading:

* Use a **queue + worker threads**
* One shared rate limiter


### 6. Best recommendation (honest answer)

If your goal is **data at scale**:

1. **Use Google Books API**
2. Cache aggressively
3. Batch requests
4. Use multithreading *only* to hide latency, not increase throughput

If you want, I can:

* Help design a **rate-limited multithreaded scraper**
* Show a **safe threading pattern in Python**
* Explain **why your 1300+ API calls still worked**

Just tell me which direction you want to go.

---