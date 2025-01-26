# RUN THE SERVER: `uvicorn main:app --reload`

# Import helper functions
from utils import scrape_website, clean_json_string, click_element, click_dropdown_option

# Playwright
from playwright.sync_api import sync_playwright
# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# LangChain
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnableMap
from langchain.prompts import ChatPromptTemplate
# URL lib
from urllib.parse import unquote
# .env library
from dotenv import load_dotenv

import json
import os

# Load env variables from .env file
load_dotenv()

# JSON Schema for structured output - not used
json_schema = {
    "title": "css_selectors",
    "description": "get css selectors",
    "type": "object",
    "properties": {
        "nextButton": {
            "type": ["string", "null"],
            "description": "CSS selector for the next button or null if absent"
        }
    },
    "additionalProperties": {
      "type": "string",
      "description": "Dynamic keys representing labels (including foreign characters) and their corresponding CSS selectors"
    },
    "required": ["nextButton"]
}

types = ['text', 'number', 'radio', 'checkbox', 'select']

field_names = [
  {'field_id': 1, 'field_name': "user_birth_date"}, 
  {'field_id': 2, 'field_name': "user_email"},
  {'field_id': 3, 'field_name': "user_name"}, 
  {'field_id': 5, 'field_name': "user_phone_number"}, 
  {'field_id': 6, 'field_name': "product_type"}
]

# Configure OpenAI model
llm = ChatOpenAI(model="gpt-4o", temperature="0.0", api_key=os.getenv("OPEN_AI_ZEALS_API_KEY"))

# Configure FastAPI
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Process the HTML content to get the list of CSS selectors for input elements and map them to their corresponding field names and types
def process_with_llm(html):
    messages = [
        SystemMessage(content="You are an AI assistant that analyzes web form input elements."),
        HumanMessage(content=f"""
                    Give me the list of the CSS selectors for these: {field_names} input elements including radio buttons from:\n\n{html}\n\n. Beware it can be a div and not just a basic input elements since it might not be semantically correct.
                    Do your best to get the closest element to the input field. 
                    Make sure the selectors are different from each other.
                    Not the labels, but the actual input elements.
                    Generate that in a JSON format with the following keys: {[{"field_id_1": "field_id_1_value", "field_name_1": "field_name_1_value", "selector": "cssSelector1" }, {"field_id_2": "field_id_2_value", "field_name_2": "field_name_2_value", "selector": "cssSelector2" }, ...]}.
                    The label will be the {field_names} under field_names. If there is none, then return empty JSON object.
                    Also include the field_id in that object.
                    Also include the type of the input element in the JSON object with a "type" field from:\n\n{types}\n\n.
                    Also include in there at the end of the JSON structure if there is a next button in the form and give me the CSS selector for that next button.
                    If there is none just add this 'nextButton': null as the value instead.
                    If there is no input elements, then just return an empty JSON object with just the nextButton key.
                    Strictly respond in a JSON format.
                    Note only include the next button and NOT a submit or a submit-like button.
                    """)
    ]
    
    # Call OpenAI API via LangChain
    response = llm.invoke(messages)
    print("\nAI Analysis of Input Elements:")
    print(response.content)
    return response.content

# Ignore, trying to experiment with chaining prompts - less accuracy because missing context in between chains
def process_with_llm_runnables_chain(html):
    extract_prompt = ChatPromptTemplate.from_template("""
      You are an AI assistant analyzing web forms.
      Give me the list of the CSS selectors for all input elements including radio buttons from:\n\n{html}\n\n. Beware it can be a div and not just a basic input elements since it might not be semantically correct.
      Do your best to get the closest element to the input field.
      If there are no input elements, then just return nothing.
    """)
    css_prompt = ChatPromptTemplate.from_template("""
      You are given the following web form elements:\n\n{elements}\n\n
      Generate that in a JSON format with the following keys: {{"label1": "cssSelector1", "label2": "cssSelector2", ... }}. 
      You can assume the label for example "First name", "Family name" or "Age etc".
      If there are no input elements, then just return an empty JSON object.
      """)
    next_button_prompt = ChatPromptTemplate.from_template("""
      Based on the given HTML:\n\n{html}\n\n
      Identify the CSS selector for a 'next' button in the form.
      If none exists, return 'nextButton': null.
      """)
    final_prompt = ChatPromptTemplate.from_template("""
      Combine the following information into a single JSON object:
      - CSS Selectors: {css_selectors}
      - Next Button Selector: {next_button}

      Ensure the JSON follows this structure:
      {{
        "label1": "cssSelector1",
        "label2": "cssSelector2",
        ...
        "nextButton": "cssSelectorForNextButton" or null
      }}
                                                    
      Strictly respond in a JSON format.                                             
      """)
    workflow = (
        RunnableMap({
            "elements": extract_prompt | llm | (lambda output: output.content),  # Extract content from AIMessage
            "html": lambda inputs: inputs["html"]
        })
        | RunnableMap({
            "css_selectors": css_prompt | llm | (lambda output: output.content),
            "html": lambda inputs: inputs["html"]
        })
        | RunnableMap({
            "next_button": next_button_prompt | llm | (lambda output: output.content),
            "css_selectors": lambda inputs: inputs["css_selectors"]
        })
        | RunnableMap({
            "final_result": final_prompt | llm | (lambda output: output.content)
        })
    )

    result = workflow.invoke({"html": html})
    print(result.get("final_result", {}))
    return result.get("final_result", {})

# Ignore, trying to experiment with chaining prompts with structured output - less accuracy because missing context in between chains
def process_with_llm_runnables_chain_structured_output(html):
    extract_prompt = ChatPromptTemplate.from_template("""
      You are an AI assistant analyzing web forms.
      Give me the list of the CSS selectors for all input elements including radio buttons from:\n\n{html}\n\n. Beware it can be a div and not just a basic input elements since it might not be semantically correct.
      Do your best to get the closest element to the input field.
      If there is no input elements, do not return anything. 
    """)
    css_prompt = ChatPromptTemplate.from_template("""
      You are given the following web form elements:\n\n{elements}\n\n
      Generate that in a JSON format with the following keys: {{"label1": "cssSelector1", "label2": "cssSelector2", ... }}. 
      You can assume the label for example "First name", "Family name" or "Age etc". The keys can be in the native language.
      """)
    next_button_prompt = ChatPromptTemplate.from_template("""
      Based on the given HTML:\n\n{html}\n\n
      Identify the CSS selector for a 'next' button in the form.
      If none exists, return 'nextButton': null.
      """)
    final_prompt = ChatPromptTemplate.from_template("""
      Combine the following information into a single JSON object:
      - CSS Selectors: {css_selectors}
      - Next Button Selector: {next_button}
      """)
    workflow = (
        RunnableMap({
            "elements": extract_prompt | llm | (lambda output: output.content),  # Extract content from AIMessage
            "html": lambda inputs: inputs["html"]
        })
        | RunnableMap({
            "css_selectors": css_prompt | llm | (lambda output: output.content),
            "html": lambda inputs: inputs["html"]
        })
        | RunnableMap({
            "next_button": next_button_prompt | llm | (lambda output: output.content),
            "css_selectors": lambda inputs: inputs["css_selectors"]
        })
        | RunnableMap({
            "final_result": final_prompt | llm.with_structured_output(json_schema) | (lambda output: output)
        })
    )

    result = workflow.invoke({"html": html})
    print(result.get("final_result", {}))
    return result.get("final_result", {})

# For calendar RPA availability
def process_calendar_llm(html):
    messages = [
        SystemMessage(content="You are an AI assistant that analyzes calendar html elements"),
        HumanMessage(content=f"""
                    Give me the the available date and time slots from the following calendar HTML:\n\n{html}\n\n.
                    List down all the free and available date and time slots.
                    The way to identify if a date and time slot is free is that it is not full, disabled, busy and does not have a class of 'full' or 'disabled' or 'busy' in its ancestor's elements'.
                    Include remaining few slots as free time slots.
                    The date is the column header and the time is in the cell.
                    Also if available, include the time ends in the time slot.
                    Also if available, include the course/product/service/lesson name in the time slot.
                    Strictly generate the response in a JSON format with the following structure:
                    {{"date1": ["time1", "time2", ...], "date2": ["time1", "time2", ...], ...}}
                    """)
    ]
    
    # Call Gemini API via LangChain
    response = llm.invoke(messages)
    print("\nAI Analysis of Calendar:")
    # print(response.content)
    return response.content


# Get the list of areas and stores' CSS selectors from a given HTML
def process_list_of_areas_and_stores(html):
    messages = [
        SystemMessage(content="You are an AI assistant that analyzes areas and/or stores from a given HTML"),
        HumanMessage(content=f"""
                    Give me the list of CSS selectors for each areas and also stores if available from the following HTML:\n\n{html}\n\n.
                    The list of areas and stores can be of div, span, input, select or option HTML elements.
                    I want the selectors for each areas and stores option.
                    Please do not include random generated selectors and disabled elements.
                    If the stores or areas are not available, then just return an empty JSON object.
                    If only either areas or stores are available, then just return the selectors for that and return an empty array for the other.
                    Strictly generate the response in a JSON format with the following structure:
                    {{"areas": ["area1_selector", "area2_selector", ...], "stores": ["store1_selector", "store2_selector", ...], ...}}
                    """)
    ]
    
    # Call Gemini API via LangChain
    response = llm.invoke(messages)
    print("\nAI Analysis of areas and stores:")
    # print(response.content)
    return response.content

# Get the list of stores' CSS selectors from a given HTML
def process_list_of_stores(html, area_selector):
    messages = [
        SystemMessage(content="You are an AI assistant that analyzes stores from a given HTML"),
        HumanMessage(content=f"""
                    Give me the list of CSS selectors for all stores if available from the following HTML:\n\n{html}\n\n.
                    The list of stores can be of div, span, input, select or option HTML elements.
                    I want the selectors for each stores option.
                    Please do not include random generated selectors and disabled elements.
                    If the stores are not available, then just return an empty array with the {area_selector} as the key.
                    Strictly generate the response in a JSON format with the following structure:
                    {{"{area_selector}": ["store1_selector", "store2_selector", ...]}}
                    """)
    ]
    
    # Call Gemini API via LangChain
    response = llm.invoke(messages)
    print("\nAI Analysis of Stores:")
    # print(response.content)
    return response.content


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to my API"}

# For getting selectors
@app.get("/api/selectors/")
def get_selectors(url: str):
    decoded_url = unquote(url)
    # Get the scraped HTML content
    html = scrape_website(decoded_url)
    
    # Step 2: Process with OpenAI API via LangChain
    if html:
      css_selectors_json = process_with_llm(html)
      try:
        # Clean the JSON string and convert it to a Python dictionary to be returned as a response
        cleaned_json = json.loads(clean_json_string(css_selectors_json))
        return {"css_selectors": cleaned_json}
      except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return {"css_selectors": "invalid JSON"}
      

# For scraping to get the dynamic content for stores from regions/prefectures
def scrape_website_and_get_stores(url, store_selector):
    with sync_playwright() as p:
        # Start a browser session
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # page.set_default_timeout(60000)

        try:
          # Navigate to the webpage
          page.goto(url, wait_until="networkidle")

          # Click the elements to get the dynamic content (using miss-paris website example)
          click_element(page, store_selector)
          html = page.evaluate(
                '''
                () => {
                    document.querySelectorAll('script, iframe, noscript, style').forEach((el) => {
                      if (el.tagName.toLowerCase() === 'script') {
                          // Remove script entirely
                          el.remove();
                      } else {
                          // Replace other elements with their children
                          const parent = el.parentNode;
                          while (el.firstChild) {
                              parent.insertBefore(el.firstChild, el);
                          }
                          parent.removeChild(el);
                      }
                  });
                  
                  // Minify the HTML
                  return document.body.outerHTML
                      .replace(/>\\s+</g, '><') // Remove spaces between tags
                      .replace(/\\n|\\t|\\r/g, '') // Remove newlines, tabs, and carriage returns
                      .replace(/\\s{2,}/g, ' ') // Replace multiple spaces with one
                      .trim(); // Trim leading/trailing whitespace
                  }
            '''
            )
            
          return html
      
        except Exception as e:
            print("Error:", e)
        
        finally:
            browser.close()
      

# Ignore, trying to experiment with structured output
@app.get("/api/selectors-structured/")
def get_selectors_structured(url: str):
    # url = "https://www.diet-undeux.jp/contact-z/"  # Replace with your target website
    decoded_url = unquote(url)
    # Step 1: Scrape Input Elements
    html = scrape_website(decoded_url)
    
    # Step 2: Process with Google Gemini via LangChain
    if html:
      # css_selectors_json = process_with_llm(html)
      css_selectors_json = process_with_llm_runnables_chain_structured_output(html)
      try:
        print(css_selectors_json)
        return {"css_selectors": css_selectors_json}
      except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return {"css_selectors": "invalid JSON"}

# For calendar RPA availability
@app.get("/api/calendar-rpa/")
def get_calendar_rpa(html_file: str):
  with open(f'calendar-html-elements/{html_file}.html', 'r', encoding='utf-8') as file:
    calendar_html = file.read()

    if calendar_html:
      res = process_calendar_llm(calendar_html)
      try:
        cleaned_json = json.loads(clean_json_string(res))
        return {"calendar_data": cleaned_json}
      except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return {"calendar_data": "invalid JSON"}
      

# For list of areas_and_stores
@app.get("/api/areas-and-stores/")
def get_areas_and_stores(url: str):
  decoded_url = unquote(url)
    # Get the scraped HTML content
  html = scrape_website(decoded_url)
  
  # Step 2: Process with OpenAI API via LangChain
  if html:
    css_selectors_json = process_list_of_areas_and_stores(html)
    try:
      # Clean the JSON string and convert it to a Python dictionary to be returned as a response
      cleaned_json = json.loads(clean_json_string(css_selectors_json))

      return {"css_selectors": cleaned_json}
    except json.JSONDecodeError as e:
      print("Invalid JSON:", e)
      return {"css_selectors": "invalid JSON"}
    

# To get dynamic stores from list of areas, to be used if the stores are not available in the initial HTML and has to be dynamically loaded
# Example usage: https://frey-a.jp/reservation/
@app.get("/api/areas-and-stores-dynamic/")
def get_areas_and_stores(url: str):
  decoded_url = unquote(url)
  # Get the scraped HTML content
  html = scrape_website(decoded_url)
  
  # Step 2: Process with OpenAI API via LangChain
  if html:
    css_selectors_json = process_list_of_areas_and_stores(html)
    try:
      # Clean the JSON string and convert it to a Python dictionary
      stores = []
      cleaned_json = json.loads(clean_json_string(css_selectors_json))

      # Extract the areas
      areas = cleaned_json.get("areas", [])
      for area in areas:
        # Click on an area selector to get the stores
        area_html = scrape_website_and_get_stores(decoded_url, area)
        # Retrieve the stores' selectors
        stores_selectors_json = process_list_of_stores(area_html, area)
        cleaned_stores_selectors_json = json.loads(clean_json_string(stores_selectors_json))
        print(cleaned_stores_selectors_json)
        # Append the stores' selectors to the list
        stores.append(cleaned_stores_selectors_json)

      return {"css_selectors": stores}
    except json.JSONDecodeError as e:
      print("Invalid JSON:", e)
      return {"css_selectors": "invalid JSON"}
    