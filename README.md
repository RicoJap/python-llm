# Scraping + LLM PoC

Simple overview of use/purpose.

## Description

- Use Playwright to scrape a given website
- Use LLM to analyse the scraped HTML contents
- Get the input elements' CSS selectors from it by using a detailed and structured prompt
- Generate a JSON response based of the LLM's output

## Getting Started

### Dependencies

* Python 3
* pip package manager
* venv

### Installing

```
pip install -r requirements.txt
```

### Executing program

```
uvicorn app_name:app --reload
```
* Server will run in port 8000

## Format

```
http://127.0.0.1:8000/api/selectors?url=<replace-this-with-url>
```


## Example
* Run using postman:

```
http://127.0.0.1:8000/api/selectors?url=https://www.diet-undeux.jp/contact-z/
```

## How to use Calendar RPA endpoint
- Go to a website in the Google Spreadsheet
- Inspect the website and get the element of the calendar
- Right click and copy the element
- Create a new file or replace current file under `calendar-html-elements` directory
- In postman, replace the query params of the GET endpoint to point to the file name without the `.html` extension