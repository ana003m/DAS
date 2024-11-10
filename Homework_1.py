import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import datetime
import math
from selenium.webdriver.common.action_chains import ActionChains
import time

url = "https://www.mse.mk/mk/stats/symbolhistory/REPl"

def get_dropdown_options(soup):
    select_element = soup.find('select', id='Code')
    options = select_element.find_all('option')
    return [option.get('value') for option in options]

def filter_options(options):
    return [opt for opt in options if not any(char.isdigit() for char in opt)]

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
options = get_dropdown_options(soup)
options = filter_options(options)

fname = os.getcwd() + "hist.csv"
if os.path.isfile(fname):
    print("Database exists")
else:
    with open(mode="w+", file="./hist.csv") as file:
        print("Created ")


df = pd.read_csv("./hist.csv", sep=';')

driver = webdriver.Firefox()

driver.get(url)

for option in options:
    select_el = driver.find_element(By.ID, 'Code')
    select = Select(select_el)
    select.select_by_visible_text(option)

    button_element = driver.find_element(By.CLASS_NAME, 'btn-primary-sm')
    button_element.click()

    table = driver.find_element(By.ID, 'resultsTable')
    rows = table.find_elements(By.TAG_NAME, "tr")

    biggest_date = df[df['Код'] == option]['Датум'].max() or datetime.datetime(1925, 1, 1)

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")

        if len(cells) > 0:
            row_date_str = cells[0].text.strip()

            try:
                row_date = datetime.datetime.strptime(row_date_str.replace('.', '-'), "%d-%m-%Y")
                
                if row_date > biggest_date:
                    row_data = f'{option}; ' + '; '.join(cell.text for cell in cells)
                    row_values = row_data.split("; ")
                    new_row = pd.DataFrame([row_values], columns=df.columns)
                    df = pd.concat([df, new_row], ignore_index=True)
        
            except ValueError:
                print(f"Skipping row with invalid date: {row_date_str}")

driver.quit()

df
