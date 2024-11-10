import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import datetime
import math
import time
from selenium.webdriver.common.action_chains import ActionChains

url = "https://www.mse.mk/mk/stats/symbolhistory/REPL"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

def get_dropdown_options(soup):
    select_element = soup.find('select', id='Code')
    options = select_element.find_all('option')
    return [option.get('value') for option in options]

def filter_options(options):
    return [code for code in options if not any(char.isdigit() for char in code)]

options = get_dropdown_options(soup)
codes = filter_options(options)

fname = os.path.join(os.getcwd(), "hist.csv")

if not os.path.isfile(fname):
    df = pd.DataFrame(columns=["Код", "Датум", "Цена", "Обем"]) 
    df.to_csv(fname, sep=';', index=False)
    print("Created <3")
else:
   
    if os.stat(fname).st_size == 0:
        print("CSV file is empty, initializing with columns.")
        df = pd.DataFrame(columns=["Код", "Датум", "Цена", "Обем"])  
    else:
        df = pd.read_csv(fname, sep=';')

driver = webdriver.Firefox()
driver.get(url)

for code in codes:
    select_el = driver.find_element(By.ID, 'Code')
    select = Select(select_el)
    select.select_by_visible_text(code)

    button_element = driver.find_element(By.CLASS_NAME, 'btn-primary-sm')
    button_element.click()

    table = driver.find_element(By.ID, 'resultsTable')
    rows = table.find_elements(By.TAG_NAME, "tr")

    biggest_date = df[df['Код'] == code]['Датум'].max()
    biggest_date = datetime.datetime(1925, 1, 1) if pd.isna(biggest_date) else datetime.datetime.strptime(biggest_date, "%d-%m-%Y")

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")

        if len(cells) > 0:
            row_date_str = cells[0].text.strip()
        
            try:
                row_date = datetime.datetime.strptime(row_date_str.replace('.', '-'), "%d-%m-%Y")
                
                if row_date > biggest_date:
                    row_data = f'{code}; ' + '; '.join(cell.text for cell in cells)
                    row_values = row_data.split("; ")
                    new_row = pd.DataFrame([row_values], columns=df.columns)

                    df = pd.concat([df, new_row], ignore_index=True)
        
            except ValueError:
                print(f"Skipping row with invalid date: {row_date_str}")

driver.quit()

biggest_date = df[df['Код'] == codes[1]]['Датум'].max()

df
