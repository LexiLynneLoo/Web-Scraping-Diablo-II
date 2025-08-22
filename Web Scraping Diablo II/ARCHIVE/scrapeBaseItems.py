'''
Created on Jun 19, 2025

@author: Lexi
'''

from bs4 import BeautifulSoup
from matplotlib import lines
import pandas as pd
from parseD2item import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from io import StringIO

#Scrape Data from Website
url = "https://www.items7.com/diablo-2-items/doc/eliteuniquehelms.html"
driver = webdriver.Chrome()
driver.get(url)
soup = BeautifulSoup(driver.page_source,'html.parser')

#Get Base Items
tables = soup.find_all('table')
table = tables[1]
df = pd.read_html(StringIO(str(table).replace('<br/>',';')))[0]
df.columns = ["Item Name", "Item Text"]

#Convert Text
for i in range(0,df.shape[0]):
    row = df["Item Text"].iloc[i]
    list = [s.strip() for s in row.split(';')]
    df.loc[i,"Item Text"] = list
for j in range(0,df.shape[0]):
    col = df.iloc[j,0]
    df.iloc[j,0] = [s.strip() for s in col.split(';')[1:3]]
print(df)
