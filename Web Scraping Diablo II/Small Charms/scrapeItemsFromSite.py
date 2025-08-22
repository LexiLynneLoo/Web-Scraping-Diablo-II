'''
Created on Jul 28, 2025

@author: Lexi Zellner

This script parses the Diablo II items7 website and scrapes listed "small charms" entries, their attributes, and prices.
The data is cleaned and then stored in the DiabloII.db database.

'''

#Import
from bs4 import BeautifulSoup
import pandas as pd
from parseD2item import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import sqlite3

#Settings
pagesToScroll = 16
url = "https://www.items7.com/diablo-2-resurrected-ladder-items-charms-small-6879.html"
#url = "https://www.items7.com/diablo-2-resurrected-items-charms-small-6356.html"

#Scrape Data from Website
driver = webdriver.Chrome()
driver.get(url)
footer = driver.find_element(By.TAG_NAME, "footer")
delta_y = footer.rect['y']
for i in range(1,pagesToScroll):
    ActionChains(driver).scroll_by_amount(0, 30*delta_y).pause(0.5).perform()
soup = BeautifulSoup(driver.page_source,'html.parser')

#Get Currency
dfMoney = pd.DataFrame(columns=["Price"])
for line in soup.find_all('p'):
    if '"price"' in str(line):
        dfMoney = pd.concat([dfMoney,pd.DataFrame({"Price":[line.get_text().replace('$','')]})], ignore_index=True)

#Get Items
df = pd.DataFrame(columns=["ItemName"])
for line in soup.find_all('div','desc'):
    df = parseD2item(line,df)

#Drop Annis and (Varies) Items
dfMoney.drop(df[df.ItemName == "Annihilus"].index, inplace=True)
df.drop(df[df.ItemName == "Annihilus"].index, inplace=True)
dfMoney.drop(df[df.ItemName == "Small Charm"].index, inplace=True)
df.drop(df[df.ItemName == "Small Charm"].index, inplace=True)
dfMoney.drop(df[df.Varies == '1'].index, inplace=True)
df.drop(df[df.Varies == '1'].index, inplace=True)
df = df.drop(columns=["AllSkills","AllAttributes","ExpGain","Unid","Varies","Lvl"])

#Combine Currency and Items
df = pd.concat([df,dfMoney],axis=1)

#Add to Database
with sqlite3.connect('DiabloII.db') as conn:
    cursor = conn.cursor()
    df.to_sql('ITEMS', conn, if_exists='append',index=False)
