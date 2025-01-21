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