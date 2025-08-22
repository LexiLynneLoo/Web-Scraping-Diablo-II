'''
Created on Jun 16, 2025

@author: Lexi
'''

from bs4 import BeautifulSoup
from matplotlib import lines
import pandas as pd
from parseD2item import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import numpy as np
from pandas.core.arrays import integer
import matplotlib.pyplot as plt

#Display Options for DataFrames
pagesToScroll = 20
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_rows', 300)

#Scrape Data from Website
#url = "https://www.items7.com/diablo-2-resurrected-ladder-items-charms-small-6879.html"
url = "https://www.items7.com/diablo-2-resurrected-items-charms-small-6356.html"
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
df = pd.DataFrame(columns=["ItemName"]) #, "ItemType"])
for line in soup.find_all('div','desc'):
    df = parseD2item(line,df)

#Filter High-Priced Items
priceArray = dfMoney["Price"].to_numpy(dtype=float,na_value=0)
indices = list(filter(lambda x: priceArray[x] > 6, range(len(priceArray))))
dfMoney = dfMoney.drop(index=indices,axis=0)
df = df.drop(index=indices,axis=0)

#Drop Annis
dfMoney.drop(df[df.ItemName == "Annihilus"].index, inplace=True)
df.drop(df[df.ItemName == "Annihilus"].index, inplace=True)
dfMoney.drop(df[df.ItemName == "Small Charm"].index, inplace=True)
df.drop(df[df.ItemName == "Small Charm"].index, inplace=True)
#df = df.drop(columns=["AllSkills","AllAttributes","ExpGain","Unid"])

#Combine Currency and Items
df = pd.concat([df,dfMoney],axis=1)
print(df.fillna(''))
print('\n')

#Linear Regression
A = df.iloc[0:df.shape[0],2:(df.shape[1])-1].to_numpy(dtype=float,na_value=0)
#np.max(A,axis=0)
b = df.iloc[0:df.shape[0],-1].to_numpy(dtype=float,na_value=0)
data = np.linalg.lstsq(A,b)
x = data[0]
s = data[3]
cols = df.columns
for i in range(0,x.size):
    print('{0: <13}'.format(cols[i+2]) + ' = ' + format(x[i],'.4f'))
print('\n')

#Reorder
dfWeights = pd.DataFrame(columns=["Stat","Weight"]) #'AllSkills','AllAttributes','ExpGain','Unid',
dfWeightList = ['MF','GF','FHR','FRW',
                'FireResist','ColdResist','LiteResist','PsnResist','AllResist',
                'Life','Mana','Str','Dex','Defense','MaxDmg','AR',
                'Psn5','Psn6','Psn9','Psn10','Psn11']
keys = df.columns.tolist()
count = 0
for col in dfWeightList:
    count = count + 1
    i = 0
    for key in keys:
        i = i + 1
        if key == col:
            ind = i
    dfWeights = pd.concat([dfWeights,pd.DataFrame({"Stat":col,"Weight":x[ind-3]},[count-1])], ignore_index=True)
    #dfWeights = pd.concat([dfWeights,pd.DataFrame({"Stat":col,"Weight":s[ind-3]},[count-1])], ignore_index=True)

#Plot Data
ax = dfWeights.plot.bar(x='Stat', y='Weight', width=1,bottom=0,edgecolor='k')
ax.get_legend().remove()
ax.set_yticks(ax.get_yticks(), labels=['${:,.3}'.format(y) for y in ax.get_yticks()])
#ax.set_yticklabels(['${:,.3}'.format(y) for y in ax.get_yticks()])
plt.title("Price of Attributes on Small Charms")
plt.ylabel('Price of Attribute')
ax.set_position([0.12,0.24,0.8,0.65])
plt.show()
